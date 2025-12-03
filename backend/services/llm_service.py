import json
import re 
import ollama
from backend.schemas.job_schemas import JobParsedData, JobMatchOutput, TailoredResumeContent
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


async def analyze_match(resume_text: str, job_data: dict) -> JobMatchOutput:
    """
    Acts as a Career Coach to analyze fit and provide strategy.
    """
    print("🤖 Service: Analyzing strategic fit...")

    prompt = f"""
    You are an honest Career Coach. Analyze if the candidate should apply for this job.
    
    JOB TITLE: {job_data.get('position_title')}
    JOB SUMMARY: {job_data.get('job_summary')}
    REQUIRED SKILLS: {job_data.get('required_skills')}
    
    CANDIDATE RESUME:
    {resume_text}
    
    TASK:
    1. Score the match (0-100).
    2. Give a verdict: "Strong Match", "Good Match", "Reach / Stretch", or "Not Recommended".
    3. Identify MISSING critical skills (dealbreakers).
    4. Provide STRATEGIC ADVICE:
       - Look for "Transferable Skills". If the job asks for a specific tool (e.g., OCI) but the candidate has the equivalent (e.g., AWS), explain EXACTLY how they should frame their experience to sound relevant.
       - If the candidate should NOT apply, explain why.
    
    ### REQUIRED JSON STRUCTURE ###
    {{
        "match_score": 0,
        "recommendation": "Strong Match", 
        "missing_critical_skills": ["Skill1", "Skill2"],
        "resume_gaps": ["Missing X", "Missing Y"],
        "transferable_skills_advice": "Your AWS experience is your strongest asset. Frame your 'Terraform for AWS' bullet as 'Infrastructure as Code for Cloud Platforms'."
    }}
    """

    response = ollama.chat(model='llama3.2:latest', messages=[
        {'role': 'user', 'content': prompt}
    ], format='json')

    return JobMatchOutput.model_validate_json(response['message']['content'])


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


# backend/services/llm_service.py

# ... imports ...

async def tailor_resume(resume_json: dict, job_data: dict) -> TailoredResumeContent:
    """
    Rewrites resume sections to emphasize TRANSFERABLE skills without fabricating experience.
    """
    print("🤖 Service: Tailoring resume (Truthfully)...")

    prompt = f"""
    You are an expert career coach. Tailor the candidate's resume for a specific job.
    
    CRITICAL RULES (DO NOT BREAK):
    1. NO FABRICATION: Do not add tools, companies, or skills the candidate does not have.
    2. NO SWAPPING: Do not change specific tool names (e.g., do NOT change 'AWS' to 'OCI').
    3. TRANSFERABLE SKILLS: If the candidate used AWS but the job needs OCI, rewrite the bullet to emphasize the *concept* (e.g., "Managed Public Cloud Infrastructure" or "Optimized Cloud Resources") rather than the specific tool.
    4. HIGHLIGHT RELEVANCE: Bring unrelated bullets closer to the job's domain (e.g., if job needs "Optimization", rephrase "Fixed bugs" to "Optimized system performance").
    
    JOB TITLE: {job_data.get('position_title')}
    REQUIRED SKILLS: {job_data.get('required_skills')}
    
    CANDIDATE EXPERIENCE (JSON):
    {resume_json.get('experience')}
    
    TASK:
    1. Write a Professional Summary that bridges the candidate's actual experience to the target role.
    2. Rewrite bullets for the 2 most relevant jobs. Focus on *actions* and *results* that apply to the new role.
    
    ### REQUIRED JSON STRUCTURE ###
    {{
        "new_summary": "<NEW_SUMMARY>",
        "rewritten_experience": {{
            "JPMorgan Chase": ["<BULLET_1>", "<BULLET_2>"],
            "Intuit": ["<BULLET_1>"]
        }},
        "match_reasoning": "Explain how you highlighted transferable skills."
    }}
    """

    response = ollama.chat(model='llama3.2:latest', messages=[
        {'role': 'user', 'content': prompt}
    ], format='json')

    content = response['message']['content']
    return TailoredResumeContent.parse_raw(content)