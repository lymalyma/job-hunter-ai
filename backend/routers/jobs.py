from fastapi import APIRouter, Depends, Body, HTTPException
from sqlmodel import Session 
from backend.db.session import get_session
from backend.schemas.job_schemas import JobParsedData
from backend.services.llm_service import extract_job_data

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