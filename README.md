# 🏹 Job Hunter AI

**A Local, Privacy-First AI Agent for Strategic Job Applications.**

Job Hunter AI is a full-stack application that acts as your personal technical recruiter and career coach. Unlike generic "cover letter generators," this tool uses **Structured Data Extraction** to deeply understand your resume and the job description, providing honest strategic advice and truthful resume tailoring.

---

## 🚀 Key Features

### 1. 📄 Structured Resume Parsing
* **PDF Ingestion:** Uploads your PDF master resume.
* **Smart Extraction:** Uses AI to convert raw text into a strict JSON schema (Contact Info, Experience, Education, Skills).
* **Section Awareness:** Understands the difference between a "Project" and a "Job," preserving data integrity.

### 2. 🔍 Job Description Analysis (ETL)
* **Messy Text Support:** Paste raw job descriptions from LinkedIn, Indeed, or email.
* **Data Cleaning:** Automatically extracts Company, Title, Salary, and Responsibilities into a clean format.
* **Human-in-the-Loop:** A UI wrapper allows you to review and edit parsed data before saving it to the local database.

### 3. 🧠 Strategic Career Coaching
* **Match Scoring:** Generates a 0-100 score based on semantic fit, not just keyword matching.
* **Gap Analysis:** Identifies specific "Dealbreaker" skills missing from your profile.
* **Transferable Skills Advice:** The AI acts as a mentor, suggesting how to frame your existing experience (e.g., *AWS*) to match target requirements (e.g., *OCI*).

### 4. ✍️ Truthful Resume Tailoring
* **No Hallucinations:** Strict prompt engineering prevents the AI from inventing experience.
* **Contextual Rewriting:** Rewrites specific bullet points to align with the job's domain language without changing the core facts of your work history.

---

## 🛠️ Tech Stack

### Backend (The Brain)
* **Framework:** Python 3.13 + **FastAPI** (Async)
* **Database:** **SQLModel** (SQLite) - Local, serverless storage.
* **AI Engine:** **Ollama** (running Llama 3.2 locally).
* **Validation:** **Pydantic** for strict Schema enforcement.
* **PDF Processing:** `pypdf`.

### Frontend (The Control Center)
* **Framework:** **React** (Vite).
* **State Management:** React Hooks (`useState`).
* **Networking:** Axios.
* **Style:** Minimalist CSS (Dark mode compatible).

---

## ⚡️ Quick Start

### Prerequisites
1.  **Ollama:** [Download Ollama](https://ollama.com/) and run the Llama 3.2 model:
    ```bash
    ollama run llama3.2
    ```
2.  **Node.js:** For the React frontend.
3.  **Python 3.10+:** For the FastAPI backend.

### 1. Setup Backend
```bash
cd job_hunter
# Create virtual env (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Run the server (from the root folder)
uvicorn backend.main:app --reload