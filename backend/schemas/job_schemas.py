from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict


class JobParsedData(BaseModel): 
    company_name: str 
    position_title: str
    salary_range: Optional[str] = "Not Listed"
    job_summary: str
    responsibilities: List[str]
    required_skills: List[str]

# REPLACE the old JobMatchOutput with this one:
class JobMatchOutput(BaseModel):
    match_score: int = Field(description="0-100 score based on keyword overlap")
    
    # The "Verdict"
    recommendation: Literal["Strong Match", "Good Match", "Reach / Stretch", "Not Recommended"]
    
    # Detailed Analysis
    missing_critical_skills: List[str] = Field(description="Dealbreakers found in the job description")
    resume_gaps: List[str] = Field(description="Specific things the resume is missing that the job asks for")
    
    # The "Strategy"
    transferable_skills_advice: str = Field(description="Strategic advice on how to relate current experience to the job")


class TailoredResumeContent(BaseModel):
    new_summary: str
    # Key = Company Name, Value = List of new bullets
    rewritten_experience: Dict[str, List[str]] 
    match_reasoning: str
