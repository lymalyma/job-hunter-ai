from typing import Optional, List 
from datetime import datetime

from sqlmodel import SQLModel, Field


class MasterResume(SQLModel, table=True): 
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    content_text: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow) 