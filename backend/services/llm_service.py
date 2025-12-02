import ollama
from backend.schemas.job_schemas import JobParsedData

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