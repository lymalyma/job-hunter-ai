from pydantic import BaseModel, Field
from typing import List, Optional

# 1. Contact Info (Header)
class ContactInfo(BaseModel):
    name: str
    phone: str
    email: str
    linkedin: Optional[str] = None

# 2. Work Experience
class WorkExperience(BaseModel):
    company: str
    job_title: str
    # Storing dates as strings is safer for parsing (e.g. "Dec 2019 - Nov 2023")
    dates: str 
    # This is the most important part for the AI Rewriter:
    bullets: List[str] = Field(description="List of responsibilities and achievements")

# 3. Education
class Education(BaseModel):
    university: str
    degree: str
    grad_date: str

# 4. Skills 
# We make this specific to YOUR resume's bold sections
class SkillSection(BaseModel):
    preferred_languages: List[str]
    tools_and_frameworks: List[str]

# 5. The Master Container
class ResumeParsedData(BaseModel):
    contact_info: ContactInfo
    experience: List[WorkExperience]
    education: List[Education]
    skills: SkillSection
    
    # Optional: A catch-all for anything else (like "Awards") just in case
    other_sections: Optional[dict] = {}

# ADD THIS CLASS:
class ResumeResponse(BaseModel):
    id: int
    filename: str
    message: str
    preview: Optional[str] = None