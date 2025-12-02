from pydantic import BaseModel 
from typing import Optional, List 


class JobParsedData(BaseModel): 
    company_name: str 
    position_title: str
    salary_range: Optional[str] = "Not Listed"
    job_summary: str
    responsibilities: List[str]
    required_skills: List[str]
