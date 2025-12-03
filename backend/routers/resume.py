from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlmodel import Session, select
from backend.db.session import get_session
from backend.models.resume import MasterResume
from backend.services.pdf_service import extract_text_from_pdf
from backend.schemas.resume_schemas import ResumeResponse

router = APIRouter()

@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...), 
    session: Session = Depends(get_session)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    content = await file.read()
    text_content = extract_text_from_pdf(content)

    if not text_content:
        raise HTTPException(status_code=400, detail="Could not extract text. PDF might be image-based")
    
    # deativate old resumes (lets keep one at a time)
    statement = select(MasterResume).where(MasterResume.is_active==True)
    existing_resumes = session.exec(statement).all()
    for res in existing_resumes: 
        res.is_active = False
        session.add(res)

    # save new resume 
    new_resume = MasterResume(
        filename=file.filename, 
        content_text=text_content, 
        is_active=True
    )

    session.add(new_resume)
    session.commit()
    session.refresh(new_resume)

    return ResumeResponse(
        id=new_resume.id, 
        filename=new_resume.filename, 
        message="Resume Uploaded successfully", 
        preview=text_content[:50] + "..."
    )