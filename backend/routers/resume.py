# backend/routers/resume.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlmodel import Session, select
from backend.db.session import get_session
from backend.models.resume import MasterResume
from backend.services.pdf_service import extract_text_from_pdf
from backend.services.llm_service import parse_resume_text # <--- Import the new service
from backend.schemas.resume_schemas import ResumeParsedData, ResumeResponse

router = APIRouter()

@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...), 
    session: Session = Depends(get_session)
):
    # 1. Validation
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    # 2. Read File & Extract Raw Text
    content = await file.read()
    text_content = extract_text_from_pdf(content)
    
    if not text_content:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    # 3. NEW: Parse into Structure (The AI Step)
    try:
        structured_data: ResumeParsedData = await parse_resume_text(text_content)
    except Exception as e:
        print(f"AI Parsing Failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse resume structure")

    # 4. Deactivate old resumes
    statement = select(MasterResume).where(MasterResume.is_active == True)
    existing_resumes = session.exec(statement).all()
    for res in existing_resumes:
        res.is_active = False
        session.add(res)

    # 5. Save to Database
    new_resume = MasterResume(
        filename=file.filename,
        content_text=text_content, # Keep raw text for searching
        
        # SAVE THE STRUCTURED JSON:
        # We save the Pydantic object as a string so we can reload it later
        parsed_json=structured_data.model_dump_json(),
        
        is_active=True
    )
    session.add(new_resume)
    session.commit()
    session.refresh(new_resume)

    return ResumeResponse(
        id=new_resume.id,
        filename=new_resume.filename,
        message="Resume uploaded and parsed successfully",
        # Show a preview of the extracted name to prove it worked
        preview=f"Parsed: {structured_data.contact_info.name} | {len(structured_data.experience)} Jobs found"
    )