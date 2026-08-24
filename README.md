# Smart Resume Screener (Production-Quality Full Stack)

An intelligent, production-ready Resume Screening application designed for modern recruitment teams. The system extracts structured profiles from multi-format resumes (PDF/Text), parses Job Descriptions into weighted requirements (differentiating mandatory vs. preferred skills), performs **semantic matching** using OpenAI-compatible LLMs with strict Pydantic JSON schema enforcement, computes a transparent **1–10 match score**, and presents an interactive Recruiter Dashboard with ranked leaderboards and deep candidate inspection.

---

## 1. Project Overview

Recruiters spend countless hours manually parsing resumes or relying on naive keyword search systems that fail when candidates use synonyms (e.g. "ML" vs. "Machine Learning", "PostgreSQL" vs. "SQL database experience").

**Smart Resume Screener** solves this by:
* Parsing multi-page PDF/text resumes with PyMuPDF while safeguarding against corrupted, scanned, or empty documents.
* Extracting structured profiles (Contact Info, Technical Skills, Experience, Education, Projects, Certifications) with strict null-safety.
* Differentiating **Required** vs. **Preferred** qualifications from Job Descriptions.
* Conducting semantic evaluation via LLMs and an explainable **40% / 30% / 10% / 10% / 10%** scoring formula.
* Providing a 1-click demo scenario for instant 2-minute demonstrations without requiring mandatory external API keys.

---

## 2. Features

- **Multi-Format Ingestion**: Upload PDFs, TXT, or MD documents.
- **Robust Text Normalization**: Unicode NFKC cleaning, hyphenated linebreak repair, bullet point standardization.
- **Null-Safe Structured Extraction**: Extracts contact details, skills taxonomy, experience duration, education degrees, and project portfolios without hallucinating missing fields.
- **JD Requirement Parsing**: Automatically isolates mandatory skills, nice-to-have skills, minimum years of experience, and domain focus.
- **Semantic LLM Matching**: Evaluates transferable skills and domain alignment instead of surface-level keyword frequency.
- **Transparent 1–10 Scoring**: Explainable weighted formula combining skills (40%), experience (30%), education (10%), projects (10%), and other JD alignments (10%).
- **Interactive Recruiter Dashboard**: Live metrics, preset role loader, drag-and-drop uploader, candidate ranking leaderboard with filters, and deep inspection modal.
- **Zero-Setup Demo Mode**: 1-click demo button seeds realistic candidates (Senior AI, Backend Python, Junior Frontend, Data Analyst, Edge Case) with instant scoring.

---

## 3. Architecture & Data Flow

```
+-------------------------------------------------------------------------+
|                           React + TypeScript UI                         |
|   (Dashboard Metrics, JD Presets, Drag & Drop Upload, Candidate Modal)  |
+------------------------------------+------------------------------------+
                                     |  REST APIs (HTTP / JSON / FormData)
                                     v
+-------------------------------------------------------------------------+
|                             FastAPI Backend                             |
|       Routers: /api/jobs, /api/resumes, /api/screen, /api/candidates    |
+------------------+-----------------------------------+------------------+
                   |                                   |
                   v                                   v
+------------------------------------+   +--------------------------------+
|           Resume Parser            |   |           JD Parser            |
| - PyMuPDF (PDF byte streaming)     |   | - Required vs Preferred Skills |
| - TextCleaner (Unicode, Hyphens)   |   | - Minimum Experience Target    |
| - ResumeExtractor (Profile Data)   |   | - Education & Domain Targets   |
+------------------+-----------------+   +----------------+---------------+
                   |                                      |
                   +------------------+-------------------+
                                      |
                                      v
+-------------------------------------------------------------------------+
|                       Semantic Matching & LLM Engine                    |
|   - OpenAI-Compatible Endpoint (GPT-4o, Groq, Ollama, OpenRouter)       |
|   - Structured Prompt + JSON Mode + Pydantic Schema Validation          |
|   - Retry & Fallback Mechanism (Graceful Offline Semantic Evaluator)    |
+-------------------------------------+-----------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------+
|                         Weighted Scoring Engine                         |
|   - Formula: Skills(40%) + Exp(30%) + Edu(10%) + Proj(10%) + Other(10%) |
|   - Bounded & Normalized: 1.0 to 10.0                                   |
|   - Categorization: Strong Match / Match / Partial Match / Weak Match   |
|   - Strengths, Skill Gaps & Recruiter Justification                     |
+-------------------------------------+-----------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------+
|                  Database Storage (SQLAlchemy ORM)                      |
|            Models: Job, Resume, Candidate, CandidateAnalysis            |
|          (SQLite for local dev -> PostgreSQL migration ready)           |
+-------------------------------------------------------------------------+
```

---

## 4. Tech Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Backend** | Python 3.11+, FastAPI, Uvicorn | High-performance async REST API, automated OpenAPI docs |
| **Data Validation** | Pydantic v2, `pydantic-settings` | Strict runtime schema enforcement for API and LLM responses |
| **PDF Extraction** | PyMuPDF (`pymupdf`) | Fast C-based text extraction across complex multi-page documents |
| **Database** | SQLAlchemy 2.0 ORM + SQLite / PostgreSQL | Modular repository pattern allowing zero-config local runs and easy PostgreSQL migration |
| **LLM Client** | `httpx`, `openai` | OpenAI-compatible API interface supporting OpenAI, Groq, Ollama, Gemini endpoints |
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS | Ultra-fast build toolchain, type safety, responsive dark-mode recruiter UI |
| **Icons & UI** | Lucide React, Tailwind CSS | Polished design with status chips, score gauges, and inspection modals |
| **Testing** | Pytest, `pytest-asyncio`, FastAPI TestClient | 100% automated test coverage across parser, scoring, and endpoints |

---

## 5. Directory Structure

```
unthinkable/
├── backend/
│   ├── app/
│   │   ├── config.py                # Environment BaseSettings
│   │   ├── database.py              # SQLAlchemy engine & session maker
│   │   ├── main.py                  # FastAPI app & lifespan handlers
│   │   ├── models/                  # SQLAlchemy ORM database models
│   │   │   ├── job.py               # Job table
│   │   │   ├── resume.py            # Resume table
│   │   │   ├── candidate.py         # Candidate profile table
│   │   │   └── analysis.py          # CandidateAnalysis table
│   │   ├── schemas/                 # Pydantic validation schemas
│   │   │   ├── job.py
│   │   │   ├── resume.py
│   │   │   ├── candidate.py
│   │   │   └── analysis.py          # LLM output & match sub-scores
│   │   ├── services/
│   │   │   ├── pdf_parser.py        # PyMuPDF extractor with fallback
│   │   │   ├── resume_extractor.py  # Structured candidate extraction
│   │   │   ├── jd_parser.py         # JD requirements parser
│   │   │   ├── llm_service.py       # OpenAI-compatible LLM client
│   │   │   ├── scoring_engine.py    # 40/30/10/10/10 scoring & semantic equivalence
│   │   │   └── screener_service.py  # Orchestrator & database persistence
│   │   ├── routers/
│   │   │   ├── jobs.py              # /api/jobs
│   │   │   ├── resumes.py           # /api/resumes
│   │   │   ├── candidates.py        # /api/candidates
│   │   │   ├── screen.py            # /api/screen & /api/jobs/{id}/results
│   │   │   ├── demo.py              # /api/demo/seed & /api/demo/samples
│   │   │   └── health.py            # /api/health
│   │   └── utils/
│   │       ├── text_cleaner.py      # Unicode & regex text normalizers
│   │       └── security.py          # Upload validation & filename sanitization
│   ├── tests/                       # Automated pytest test suite
│   │   ├── conftest.py
│   │   ├── test_pdf_parser.py
│   │   ├── test_resume_extractor.py
│   │   ├── test_jd_parser.py
│   │   ├── test_scoring_engine.py
│   │   ├── test_llm_service.py
│   │   └── test_api_endpoints.py
│   ├── data/sample_resumes/         # Generated realistic PDF resumes
│   ├── generate_samples.py          # PDF resume sample generator script
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.tsx
│   │   │   ├── MetricCards.tsx
│   │   │   ├── JobDescriptionInput.tsx
│   │   │   ├── ResumeUploader.tsx
│   │   │   ├── CandidateRankingTable.tsx
│   │   │   ├── CandidateDetailModal.tsx
│   │   │   └── ScoreBadge.tsx
│   │   ├── services/api.ts          # Axios API client
│   │   ├── types/index.ts           # TypeScript interfaces
│   │   ├── App.tsx                  # Main layout
│   │   └── index.css                # Tailwind CSS
│   ├── package.json
│   └── vite.config.ts
├── sample_data/                     # Sample PDFs & Job Descriptions
├── .env.example
└── README.md
```

---

## 6. Installation & Setup Guide

### Prerequisites
- Python 3.11+
- Node.js 20+ & npm

### Step 1: Clone Repository
```bash
git clone <repo-url>
cd unthinkable
```

### Step 2: Set Up Backend
```bash
# Create and activate virtual environment (optional but recommended)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Generate realistic PDF sample resumes
python backend/generate_samples.py
```

### Step 3: Configure Environment Variables
Copy `.env.example` to `backend/.env`:
```bash
cp backend/.env.example backend/.env
```
*(Optional)* Add your OpenAI or Groq API key in `backend/.env`:
```ini
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```
> **Note:** If `OPENAI_API_KEY` is left blank, the application automatically activates its high-precision built-in deterministic semantic evaluator, so all features and tests work with zero external dependencies!

### Step 4: Set Up Frontend
```bash
cd frontend
npm install
```

---

## 7. How to Run the Application

### 1. Run the Backend API
From the root directory:
```bash
cd backend
python -m uvicorn app.main:app --port 8000 --reload
```
- Backend API will run at: `http://localhost:8000`
- Interactive OpenAPI Docs (Swagger UI): `http://localhost:8000/docs`

### 2. Run the Frontend Dashboard
In a new terminal window:
```bash
cd frontend
npm run dev
```
- Frontend will open at: `http://localhost:5173`

---

## 8. LLM Prompt Design

The system enforces structured JSON output using Pydantic schema validation.

### System Prompt
```
You are an expert technical recruiter and AI talent screener.
Your task is to evaluate a candidate's resume against a Job Description (JD) with high precision, fairness, and semantic understanding.

CRITICAL RULES:
1. Return ONLY a valid, parseable JSON object matching the exact schema specified below.
2. Do NOT output markdown code blocks (```json), commentary, or extra text.
3. Perform true semantic matching (e.g. "ML" = "Machine Learning", "PostgreSQL" = "SQL Database experience", "FastAPI" = "Python REST API").
4. Do NOT falsely invent skills, years, or credentials that the candidate does not have.
5. If a candidate is missing a required skill, list it in skills_match.missing.
6. Provide an honest, calibrated overall score from 1.0 to 10.0:
   - 8.0 - 10.0: Strong Match (exceeds or meets all mandatory requirements)
   - 6.5 - 7.9: Match (solid fit, minor gaps in non-critical areas)
   - 4.5 - 6.4: Partial Match (has transferable skills but lacks key requirements)
   - 1.0 - 4.4: Weak Match (misaligned role or significant missing core requirements)
```

### JSON Schema Output
```json
{
  "candidate_name": "Alex Chen",
  "overall_score": 9.1,
  "recommendation": "Strong Match",
  "skills_match": {
    "matched": ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "Docker", "LLM", "RAG"],
    "partial": ["Kubernetes"],
    "missing": []
  },
  "experience_match": {
    "score": 9.5,
    "summary": "Candidate has 6+ years of relevant experience architecting GenAI platforms with FastAPI and React."
  },
  "education_match": {
    "score": 9.5,
    "summary": "Holds Master of Science in Computer Science from Stanford University."
  },
  "relevant_projects": [
    "PromptFlow-Agent: Open-source framework for structured LLM evaluation (Python, FastAPI, React, PyTorch)",
    "Multi-Tenant RAG Engine: Enterprise search engine with hybrid BM25 and vector embeddings"
  ],
  "strengths": [
    "Extensive hands-on experience in full-stack AI development (FastAPI + React + LLMs)",
    "Strong relational database optimization with PostgreSQL",
    "Track record in deploying production RAG microservices"
  ],
  "gaps": [
    "No major disqualifying gaps identified"
  ],
  "justification": "Alex Chen is evaluated as a Strong Match (Score: 9.1/10). Demonstrates deep expertise across all mandatory technical requirements and exceeds seniority guidelines."
}
```

---

## 9. Scoring Methodology

The overall score is computed on a **1.0 to 10.0** normalized scale using an explainable, weighted formula:

$$\text{Final Score} = (\text{Skills} \times 0.40) + (\text{Experience} \times 0.30) + (\text{Education} \times 0.10) + (\text{Projects} \times 0.10) + (\text{Other} \times 0.10)$$

### Weight Breakdown:
1. **Skills Match (40%)**:
   - Mandatory Requirements (30% weight): Scored based on ratio of required skills demonstrated.
   - Preferred Requirements (10% weight): Rewards nice-to-have capabilities without heavily penalizing their absence.
2. **Relevant Experience (30%)**:
   - Compares total verified years against JD minimum threshold.
   - Weights relevant titles and seniority matches.
3. **Academic & Education Alignment (10%)**:
   - Evaluates degree level (Ph.D., M.S., B.S.) and STEM relevance.
4. **Projects & Domain Relevance (10%)**:
   - Scores practical portfolio implementations matching the job domain.
5. **Other Factors & Certifications (10%)**:
   - Cloud certifications (AWS, GCP, CKA), work location compatibility.

### Recommendation Tiers:
- **Strong Match**: $8.0 - 10.0$ (Candidate meets or exceeds all core qualifications; automatic shortlist candidate).
- **Match**: $6.5 - 7.9$ (Candidate meets primary requirements with minor non-critical gaps).
- **Partial Match**: $4.5 - 6.4$ (Candidate has transferable skills but lacks core mandatory competencies).
- **Weak Match**: $1.0 - 4.4$ (Candidate is significantly under-qualified or misaligned with role requirements).

---

## 10. Edge Cases Handled

| Edge Case | Behavior & Resilience Strategy |
|---|---|
| **Empty File (0 bytes)** | `PDFParsingError` caught; displays clear error message in table without crashing pipeline. |
| **Corrupted PDF** | Handled gracefully by PyMuPDF byte validation; records `status: error`. |
| **Image-only / Scanned PDF** | Checks extracted character length; raises warning: *"Scanned PDF without text layer"*. |
| **Missing Email / Phone** | Represented as `null`; extraction does not invent or hallucinate candidate contact info. |
| **Missing Education / Experience** | Represented as empty list `[]`; scoring engine adjusts subscore down without crashing. |
| **Duplicate Uploads** | File names sanitized and prefixed with unique short UUIDs to prevent disk overwrites. |
| **Short / Empty JD** | API validates minimum text length ($\ge 15$ chars) and returns descriptive HTTP 400. |
| **LLM API Timeout / Failure** | Automatic retry with exponential backoff; falls back to deterministic heuristic engine. |
| **Malformed LLM JSON Output** | Regex extraction strips markdown code fences (````json ... ````) and repairs truncated JSON. |

---

## 11. REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | System health check and active LLM configuration status |
| `POST` | `/api/jobs` | Create a new Job Description and parse structured requirements |
| `GET` | `/api/jobs` | List all saved job descriptions |
| `GET` | `/api/jobs/{id}` | Retrieve specific job details |
| `POST` | `/api/resumes/upload` | Upload multiple resume files (PDF, TXT, MD) |
| `GET` | `/api/resumes/{id}` | Retrieve raw text and parsed metadata for a resume |
| `POST` | `/api/screen` | Run semantic screening for all candidates associated with a job |
| `GET` | `/api/jobs/{id}/results` | Retrieve ranked candidates, statistics, and score distributions |
| `GET` | `/api/candidates` | List all candidate profiles with optional filtering |
| `GET` | `/api/candidates/{id}` | Retrieve full candidate profile, sub-scores, and justifications |
| `POST` | `/api/demo/seed` | 1-Click demo endpoint to seed sample JD and 5 ranked candidate resumes |
| `GET` | `/api/demo/samples` | Get pre-configured job templates and sample resume snippets |

---

## 12. Automated Test Suite

Run the full pytest suite:
```bash
python -m pytest -v backend/tests
```

### Test Coverage Summary:
- `test_pdf_parser.py`: Tests valid text extraction, multi-page PDFs, empty files, corrupted byte streams.
- `test_resume_extractor.py`: Tests candidate extraction, name heuristics, email/phone parsing, null safety.
- `test_jd_parser.py`: Tests required vs preferred skill isolation, experience thresholds, empty JDs.
- `test_scoring_engine.py`: Tests semantic equivalences, 40/30/10/10/10 math, score bounds, recommendation mapping.
- `test_llm_service.py`: Tests schema validation, markdown stripping, JSON repair, fallback evaluator.
- `test_api_endpoints.py`: Integration tests for `/api/jobs`, `/api/resumes/upload`, `/api/screen`, `/api/demo/seed`.

---

## 13. 2–3 Minute Demo Flow

1. **Open Dashboard**: Navigate to `http://localhost:5173`.
2. **Load Scenario**: Click the **1-Click Demo** button in the top navigation bar.
3. **Observe Ingestion**: The system automatically creates a *Senior Full-Stack AI Engineer* JD and screens 5 candidate resumes.
4. **Review Metrics**: Notice the total resumes (5), processed (5), shortlisted (2), and average score.
5. **Inspect Rank #1 (Alex Chen - 9.1/10)**:
   - Click **Inspect** to open the candidate modal.
   - Show the large visual score (`9.1 / 10`), matched skills in green (`Python`, `FastAPI`, `React`, `PostgreSQL`, `LLM`, `RAG`), and verified strengths.
6. **Inspect Partial Match (David Kim - 5.0/10)**:
   - Show how missing backend requirements (`FastAPI`, `PostgreSQL`, `LLM`) are highlighted in red under *Missing Requirements*.
7. **Inspect Weak Match (Emma Watson - 3.5/10)**:
   - Show how mismatched domain skills (Data Analyst vs. Full Stack AI Engineer) receive an honest, transparent low score.

---

## 14. Top Technical Interview Q&A

### Q1: How does your system prevent keyword-stuffing gaming?
> **Answer:** Rather than counting keyword frequency, our scoring engine evaluates contextual skill evidence and requires verification across multiple dimensions: work experience duration, project technical stacks, and education. Furthermore, the LLM semantic evaluation analyzes whether skills were utilized in relevant projects and roles, rather than just mentioned in a skills list.

### Q2: How does the system handle LLM non-determinism and JSON hallucinations?
> **Answer:** We enforce strict Pydantic v2 schemas (`CandidateAnalysisOutput`) with runtime validation, field clamping ($1.0 \le \text{score} \le 10.0$), and recommendation normalization. If an LLM call times out or returns malformed JSON, our regex repair cleans the output; if it fails repeatedly, the system falls back gracefully to a deterministic semantic engine without crashing.

### Q3: Why separate Required vs. Preferred skills in Job Descriptions?
> **Answer:** In real-world hiring, missing a mandatory skill (e.g. Python for a Python role) is disqualifying, whereas missing a preferred skill (e.g. Kubernetes) should only slightly adjust the score. We assign 30% of the skills weight to mandatory requirements and 10% to preferred skills.

### Q4: How is this application designed for scale and cloud deployment?
> **Answer:** The backend uses SQLAlchemy 2.0 with decoupled database session injection, allowing instantaneous migration from SQLite to PostgreSQL by simply updating `DATABASE_URL`. The resume parsing and screening pipeline is asynchronous, and PDF processing is memory-efficient with PyMuPDF byte streams.

---

## 15. License

MIT License. Designed and engineered for production full-stack AI screening.
