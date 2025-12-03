import json 

from fastapi import APIRouter, Depends, Body, HTTPException
from sqlmodel import Session, select
from backend.db.session import get_session
from backend.schemas.job_schemas import JobParsedData, JobMatchOutput, TailoredResumeContent
from backend.services.llm_service import extract_job_data, analyze_match, tailor_resume
from backend.models.job import Job
from backend.models.resume import MasterResume


# create router 
router = APIRouter() 


@router.post("/parse", response_model=JobParsedData)
async def parse_job_description(
    raw_text: str = Body(..., embed=True), 
    session: Session = Depends(get_session)
):
    """
    Endpoint: POST /jobs/parse
    Payload: { "raw_text": "We are looking for a python dev..." }
    """
    if not raw_text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        # Call the Service Layer
        parsed_data = await extract_job_data(raw_text)
        
        # Note: We haven't saved to DB yet, we just return the analysis 
        # so the user can review it in the UI first.
        return parsed_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/", response_model=Job)
async def create_job(
    job_data: JobParsedData, 
    session: Session=Depends(get_session)
):
    try: 
        # convert the pydantic model to the SQLModel
        job = Job(
            company_name=job_data.company_name, 
            position_title=job_data.position_title, 
            salary_range=job_data.salary_range, 
            job_summary=job_data.job_summary, 
            raw_description=job_data.model_dump_json())
        
        session.add(job)
        session.commit() 
        session.refresh(job)

        return job 
    
    except Exception as e: 
        raise HTTPException(status_code=500, detail=str(e)) 
    
# Analyzing endpoint 

@router.post("/{job_id}/analyze", response_model=JobMatchOutput)
async def analyze_job_fit(
    job_id: int, 
    session: Session = Depends(get_session)
):
    # A. Fetch Job
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # B. Fetch Active Resume
    statement = select(MasterResume).where(MasterResume.is_active == True)
    resume = session.exec(statement).first()
    
    if not resume:
        raise HTTPException(status_code=400, detail="No active resume found")

    # C. Prepare Data
    job_dict = {
        "position_title": job.position_title,
        "job_summary": job.job_summary,
        "required_skills": job.raw_description 
    }
    
    # D. Run Analysis
    match_result = await analyze_match(resume.content_text, job_dict)
    
    # E. Save Score (We only store the int score in DB for now)
    job.match_score = match_result.match_score
    session.add(job)
    session.commit()
    
    return match_result


@router.post("/{job_id}/tailor", response_model=TailoredResumeContent)
async def tailor_job_resume(
    job_id: int, 
    session: Session = Depends(get_session)
):
    # A. Fetch Job
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # B. Fetch Active Resume
    statement = select(MasterResume).where(MasterResume.is_active == True)
    resume = session.exec(statement).first()
    
    if not resume or not resume.parsed_json:
        raise HTTPException(status_code=400, detail="No parsed resume found. Please re-upload your resume.")

    # C. Prepare Data
    # Load the JSON string from DB back into a real Python Dictionary
    resume_dict = json.loads(resume.parsed_json)
    
    job_dict = {
        "position_title": job.position_title,
        "required_skills": job.raw_description
    }
    
    # D. Run AI
    tailored_content = await tailor_resume(resume_dict, job_dict)
    
    return tailored_content