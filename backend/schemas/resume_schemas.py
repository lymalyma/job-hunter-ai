from pydantic import BaseModel 
from typing import Optional 

class ResumeResponse(BaseModel): 
    id: int 
    filename: str 
    message: str 
    preview: Optional[str]