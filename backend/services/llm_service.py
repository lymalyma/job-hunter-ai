import json
import re 
import ollama
from backend.schemas.job_schemas import JobParsedData, JobMatchOutput
from backend.schemas.resume_schemas import ResumeParsedData


async def extract_job_data(raw_text: str) -> JobParsedData:
    """
    Sends raw text to Ollama and returns structured Pydantic data.
    """
    print("🤖 Service: Sending text to Ollama...")

    prompt = f"""
    You are a data extraction assistant. Analyze the following job description.
    Extract: Company Name, Position Title, Salary, Summary, Responsibilities, and Skills.
    
    RETURN ONLY VALID JSON matching this structure:
    {{
        "company_name": "string",
        "position_title": "string",
        "salary_range": "string or 'Not Listed'",
        "job_summary": "1 sentence summary",
        "responsibilities": ["Start with action verbs", "e.g., Design APIs"], 
        "required_skills": ["Python", "AWS", "SQL"]
    }}

    Raw Job Description:
    {raw_text}
    """

    # Using llama3.2 is great - it's faster for this kind of extraction!
    response = ollama.chat(model='llama3.2:latest', messages=[
        {'role': 'user', 'content': prompt}
    ], format='json')

    return JobParsedData.parse_raw(response['message']['content'])


# backend/services/llm_service.py

# ... keep imports ...

async def analyze_match(resume_text: str, job_data: dict) -> JobMatchOutput:
    """
    Compares the Master Resume against the Parsed Job Data.
    """
    print("🤖 Service: Comparing Resume vs Job...")

    prompt = f"""
    You are a technical recruiter. Compare the Candidate's Resume against the Job Description.
    
    TASK:
    1. MATCH SCORE: 0-100 based on keyword overlap.
    2. MISSING SKILLS: Identify important technical skills in the Job that are missing from the Resume.
    3. FEEDBACK: Write a specific 1-sentence explanation of the score.
    
    CRITICAL: DO NOT COPY THE EXAMPLE TEXT. WRITE ORIGINAL FEEDBACK.

    ### REQUIRED JSON STRUCTURE ###
    {{
        "match_score": <INTEGER_0_TO_100>,
        "missing_skills": ["<MISSING_SKILL_1>", "<MISSING_SKILL_2>"],
        "analysis_feedback": "<WRITE_YOUR_OWN_FEEDBACK_HERE>"
    }}

    --- JOB DETAILS ---
    Title: {job_data.get('position_title')}
    Skills Needed: {job_data.get('required_skills')}
    Summary: {job_data.get('job_summary')}

    --- CANDIDATE RESUME ---
    {resume_text}
    """

    response = ollama.chat(model='llama3.2:latest', messages=[
        {'role': 'user', 'content': prompt}
    ], format='json')

    return JobMatchOutput.parse_raw(response['message']['content'])


def clean_json_text(text: str) -> str:
    """
    Fixes common AI JSON mistakes:
    1. Replaces smart quotes (“ ”) with straight quotes (" ").
    2. Removes Markdown code blocks (```json ... ```).
    """
    # Remove markdown code fences if present
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*$", "", text)
    
    # Fix smart quotes/apostrophes
    text = text.replace("“", '"').replace("”", '"').replace("’", "'")
    
    return text.strip()

async def parse_resume_text(resume_text: str) -> ResumeParsedData:
    """
    Converts raw resume text into a structured JSON object.
    """
    print("🤖 Service: Parsing resume structure...")

    prompt = f"""
        You are a data extraction assistant. Convert the resume text below into strict JSON.
        
        INSTRUCTIONS:
        1. Extract 'contact_info', 'experience', 'education', and 'skills'.
        2. For 'experience', create a LIST of objects. Close the list ']' before starting 'education'.
        3. Use standard quotes (") not smart quotes (“).
        
        ### REQUIRED JSON STRUCTURE ###
        {{
            "contact_info": {{ 
                "name": "<EXTRACT_NAME>", 
                "phone": "<EXTRACT_PHONE>", 
                "email": "<EXTRACT_EMAIL>", 
                "linkedin": "<EXTRACT_LINKEDIN>" 
            }},
            "experience": [
                {{ 
                    "company": "<EXTRACT_COMPANY>", 
                    "job_title": "<EXTRACT_TITLE>", 
                    "dates": "<EXTRACT_DATES>", 
                    "bullets": ["<EXTRACT_BULLET_1>", "<EXTRACT_BULLET_2>"] 
                }}
            ], 
            "education": [
                {{ "university": "<EXTRACT_UNIVERSITY>", "degree": "<EXTRACT_DEGREE>", "grad_date": "<EXTRACT_DATE>" }}
            ],
            "skills": {{
                "preferred_languages": ["<EXTRACT_LANGUAGE>"],
                "tools_and_frameworks": ["<EXTRACT_TOOL>"]
            }}
        }}

        --- RESUME TEXT ---
        {resume_text}
        """

    response = ollama.chat(model='llama3.2:latest', messages=[
        {'role': 'user', 'content': prompt}
    ], format='json')

    raw_content = response['message']['content']
    
    # 1. Clean the text (Fix the quotes!)
    cleaned_content = clean_json_text(raw_content)
    
    # DEBUG: Print cleaned content to check if brackets are fixed
    print(f"DEBUG CLEANED JSON: {cleaned_content[:200]}...") 

    return ResumeParsedData.model_validate_json(cleaned_content)