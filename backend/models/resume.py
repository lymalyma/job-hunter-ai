# backend/models/resume.py
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class MasterResume(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    
    # 1. We keep the raw text as a backup (for simple searches)
    content_text: str 
    
    # 2. NEW: We add a field to store the Structured JSON
    parsed_json: Optional[str] = Field(default=None, description="Stores the ResumeParsedData as a JSON string")
    
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)