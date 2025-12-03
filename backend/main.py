from fastapi import FastAPI
# FIX 1: Use absolute imports so Python knows exactly where to look
from backend.db.session import create_db_and_tables
from backend.routers import jobs, resume 

app = FastAPI(title="Job Hunter AI")

@app.on_event("startup")
def on_startup(): 
    create_db_and_tables()

app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
app.include_router(resume.router, prefix="/resume", tags=["Resume"])