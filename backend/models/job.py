from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Job(SQLModel, table=True): 
    id: Optional[int] = Field(default=None, primary_key=True)
    company_name: str
    position_title: str 
    salary_range: Optional[str] = None 
    job_summary: str 
    raw_description: str 
    match_score: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
     