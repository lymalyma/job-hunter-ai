import ollama
from backend.schemas.job_schemas import JobParsedData, JobMatchOutput

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
    Compares the Master Resume against the Parsed Job Data.
    """
    print("🤖 Service: Comparing Resume vs Job...")

    prompt = f"""
    You are a technical recruiter. Compare the Candidate's Resume against the Job Description.
    
    1. MATCH SCORE: Give a score from 0-100 based on skills and experience overlap.
    2. MISSING SKILLS: List specific technical keywords found in the Job but NOT in the Resume.
    3. FEEDBACK: 1 sentence explaining the score.

    RETURN ONLY VALID JSON matching this structure:
    {{
        "match_score": 85,
        "missing_skills": ["Kubernetes", "GraphQL"],
        "analysis_feedback": "Strong Python experience, but missing containerization tools."
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