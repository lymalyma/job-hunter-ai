from fastapi import APIRouter, Depends, Body, HTTPException
from sqlmodel import Session, select
from backend.db.session import get_session
from backend.schemas.job_schemas import JobParsedData, JobMatchOutput
from backend.services.llm_service import extract_job_data, analyze_match
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

# This uses the saved Job ID to run the comparison against your active resume
@router.post("/{job_id}/analyze", response_model=JobMatchOutput)
async def analyze_job_fit(
    job_id: int, 
    session: Session = Depends(get_session)
):
    # A. Fetch the Job
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # B. Fetch the Active Resume
    # We find the resume marked is_active=True
    statement = select(MasterResume).where(MasterResume.is_active == True)
    resume = session.exec(statement).first()
    
    if not resume:
        raise HTTPException(status_code=400, detail="No active resume found. Please upload one first.")

    # C. Prepare Data for AI
    # We need to reconstruct the dictionary from the job object to pass to the AI
    job_dict = {
        "position_title": job.position_title,
        "job_summary": job.job_summary,
        "required_skills": job.raw_description # Passing the full dump so AI sees responsibilities too
    }
    
    # D. Run Analysis
    try:
        match_result = await analyze_match(resume.content_text, job_dict)
        
        # E. Save the Score to the DB
        job.match_score = match_result.match_score
        session.add(job)
        session.commit()
        
        return match_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
