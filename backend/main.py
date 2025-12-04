from fastapi import FastAPI
# FIX 1: Use absolute imports so Python knows exactly where to look
from backend.db.session import create_db_and_tables
from backend.routers import jobs, resume 
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Job Hunter AI")

origins = [
    "http://localhost:5173", # Vite (React) default port
    "http://localhost:3000", # Create React App default port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow POST, GET, OPTIONS, etc.
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup(): 
    create_db_and_tables()

app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
app.include_router(resume.router, prefix="/resume", tags=["Resume"])