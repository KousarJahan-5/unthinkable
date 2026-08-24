import os
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.job import Job
from app.models.resume import Resume
from app.models.candidate import Candidate
from app.models.analysis import CandidateAnalysis
from app.services.screener_service import ScreenerService

router = APIRouter(prefix="/api/demo", tags=["Demo & Seeding"])

SAMPLE_JD_SENIOR_AI_FULLSTACK = """
Senior Full-Stack AI Engineer

About the Role:
We are seeking an experienced Senior Full-Stack AI Engineer to design and deploy scalable GenAI web applications. You will architect robust Python/FastAPI microservices, build responsive React TypeScript user interfaces, and integrate cutting-edge LLMs and RAG pipelines.

Required Qualifications:
- 5+ years of software engineering experience.
- Strong proficiency in Python and modern web frameworks (FastAPI or Django).
- Hands-on expertise with React, TypeScript, and modern frontend state management.
- Deep practical experience with LLMs, Prompt Engineering, RAG (Retrieval Augmented Generation), and vector search.
- Strong relational database design skills with PostgreSQL or SQL.
- Experience with Docker containerization and CI/CD pipelines.
- Bachelor's or Master's degree in Computer Science or related STEM discipline.

Preferred / Nice to Have:
- Experience with PyTorch or TensorFlow model fine-tuning.
- Kubernetes (K8s) deployment experience on AWS or GCP.
- Contributions to open-source AI or full-stack projects.

Core Responsibilities:
- Build low-latency RESTful APIs and real-time streaming endpoints for AI applications.
- Design intuitive recruiter and candidate dashboards with React & Tailwind CSS.
- Optimize LLM prompt chains, implement structured schema validation, and benchmark semantic accuracy.
- Collaborate with product and design teams in an Agile/Scrum environment.
"""

SAMPLE_JD_BACKEND_PYTHON = """
Senior Python Backend Engineer

About the Role:
We are looking for a Senior Backend Engineer to architect high-throughput distributed backend services.

Required Qualifications:
- 4+ years of professional backend development with Python (FastAPI / Django).
- Strong knowledge of PostgreSQL, database optimization, and Redis caching.
- Experience with microservices, Docker, and RESTful API architecture.
- Solid understanding of Git, CI/CD, and automated testing (pytest).

Preferred Qualifications:
- AWS or GCP cloud infrastructure experience.
- Experience with Kafka or message queues.
- Basic knowledge of machine learning pipelines.
"""

SAMPLE_RESUMES_DATA = [
    {
        "filename": "Alex_Chen_Senior_AI_FullStack.txt",
        "text": """
Alex Chen
San Francisco, CA | alex.chen@techmail.dev | +1 (415) 555-0192 | linkedin.com/in/alexchen-ai | github.com/alexchen-dev

SUMMARY:
Staff / Senior Full-Stack AI Engineer with 6+ years of experience designing and deploying enterprise GenAI systems, high-throughput FastAPI microservices, and React TypeScript web platforms. Led architecture for RAG systems serving 2M+ monthly queries.

TECHNICAL SKILLS:
- Languages: Python, TypeScript, JavaScript, SQL, C++
- Frontend: React, Next.js, Tailwind CSS, Redux Toolkit, HTML5/CSS3
- Backend & APIs: FastAPI, Django, Node.js, RESTful APIs, gRPC, Celery
- AI & LLMs: Large Language Models (LLM), RAG, LangChain, LlamaIndex, OpenAI, Hugging Face, PyTorch, Vector Databases
- Databases & Storage: PostgreSQL, Redis, MongoDB, SQLite
- Cloud & DevOps: AWS (EC2, S3, RDS), Docker, Kubernetes, CI/CD, GitHub Actions
- Practices: Agile, Scrum, TDD, Pytest, System Design

PROFESSIONAL EXPERIENCE:
Senior Full-Stack AI Engineer | NeuralScale AI | 2021 - Present
- Architected and shipped an enterprise GenAI platform using FastAPI, Python, and React TypeScript, reducing workflow latency by 45%.
- Implemented hybrid vector search RAG pipeline utilizing PostgreSQL (pgvector) and OpenAI embeddings with 94% precision.
- Containerized microservices using Docker and orchestrated deployments on AWS ECS and Kubernetes with automated CI/CD pipelines.
- Mentored 5 junior engineers in prompt engineering, structured JSON output validation, and frontend state management.

Full-Stack Developer | Apex Software Labs | 2018 - 2021
- Developed responsive web applications in React and FastAPI backed by PostgreSQL.
- Designed REST APIs handling 5,000+ requests per second with Redis caching.
- Integrated automated testing suites with pytest achieving 92% code coverage.

EDUCATION:
- Master of Science (M.S.) in Computer Science | Stanford University | 2018
- Bachelor of Science (B.S.) in Computer Science | UC Berkeley | 2016

PROJECTS:
- PromptFlow-Agent: Open-source framework for structured LLM evaluation and schema validation (Tech: Python, FastAPI, React, PyTorch).
- Multi-Tenant RAG Engine: Scalable enterprise search engine with hybrid BM25 and vector embeddings (Tech: Python, PostgreSQL, Docker, AWS).

CERTIFICATIONS:
- AWS Certified Solutions Architect - Associate
"""
    },
    {
        "filename": "Sarah_Jenkins_Backend_Python.txt",
        "text": """
Sarah Jenkins
Austin, TX | sarah.jenkins@workmail.io | +1 (512) 555-0144 | github.com/sjenkins-code

PROFESSIONAL SUMMARY:
Senior Python Backend Developer with 5 years of experience building resilient microservices, optimizing PostgreSQL databases, and maintaining CI/CD pipelines in AWS.

SKILLS:
- Languages: Python, SQL, Bash
- Frameworks: FastAPI, Django, Flask, SQLAlchemy
- Databases: PostgreSQL, MySQL, Redis
- Infrastructure: Docker, AWS (S3, EC2), CI/CD, Git, GitHub Actions
- Testing: Pytest, TDD, Unit Testing

WORK EXPERIENCE:
Backend Engineer | CloudMatrix Systems | 2020 - Present
- Developed high-throughput REST APIs using Python, FastAPI, and PostgreSQL.
- Optimized database indexing and queries, cutting query execution times by 35%.
- Built automated CI/CD workflows using GitHub Actions and Docker containers.
- Implemented Celery worker queues for asynchronous email and report generation.

Software Developer | DataStream Corp | 2019 - 2020
- Built Django web applications with relational database backends.
- Wrote extensive unit tests using pytest.

EDUCATION:
- Bachelor of Science (B.S.) in Software Engineering | University of Texas at Austin | 2019

PROJECTS:
- Async-DB-Broker: Lightweight connection pooler for PostgreSQL in Python.
- Micro-Cache: Distributed in-memory caching wrapper using Redis.
"""
    },
    {
        "filename": "David_Kim_Junior_Frontend.txt",
        "text": """
David Kim
Seattle, WA | david.kim@webdev.net | +1 (206) 555-0188 | github.com/davidkim-ui

PROFILE:
Junior Frontend Developer with 1.5 years of experience building clean, responsive user interfaces using React, JavaScript, HTML, and CSS. Passionate about UI/UX and web performance.

TECHNICAL SKILLS:
- Frontend: React, JavaScript, HTML5, CSS3, Tailwind CSS
- Tools: Git, GitHub, VS Code, Figma, Webpack
- Basic familiarity: Node.js, Express, REST APIs

EXPERIENCE:
Junior Web Developer | PixelCraft Media | 2023 - Present
- Created responsive landing pages and dashboard components using React and Tailwind CSS.
- Collaborated with UI/UX designers to translate Figma prototypes into pixel-perfect components.
- Maintained code repositories using Git and GitHub.

EDUCATION:
- Bachelor of Arts (B.A.) in Digital Arts and Media | University of Washington | 2023

PROJECTS:
- React-Task-Dashboard: Kanban task board with drag-and-drop support (React, Tailwind).
- Weather-Widget-App: Dynamic weather lookup using OpenWeather API (JavaScript, React).
"""
    },
    {
        "filename": "Emma_Watson_Data_Analyst.txt",
        "text": """
Emma Watson
Chicago, IL | emma.watson@analyticsdata.org | +1 (312) 555-0177

SUMMARY:
Data Analyst with 3 years of experience generating business intelligence dashboards, SQL queries, and statistical reports in Excel and Tableau.

SKILLS:
- Data Analysis: SQL, Excel, Tableau, Power BI, Google Sheets
- Statistics: Data Cleaning, Business Intelligence, Reporting, A/B Testing
- Basic Python: Pandas, Data visualization

EXPERIENCE:
Data Analyst | Midwest Retail Group | 2021 - Present
- Formulated complex SQL queries to extract customer transaction records from MySQL.
- Built interactive Tableau executive dashboards tracking quarterly sales and KPI metrics.
- Cleaned and prepared monthly reporting datasets for marketing stakeholders.

EDUCATION:
- Bachelor of Science (B.S.) in Business Analytics | University of Illinois | 2021

PROJECTS:
- Retail Sales KPI Tracker: Tableau dashboard visualizing seasonal sales trends.
"""
    },
    {
        "filename": "Edge_Case_Minimal_Profile.txt",
        "text": """
Jordan Taylor
Self-taught developer looking for opportunities in web development.
Skills: Python, HTML, CSS.
Projects: Built a personal blog with Python.
"""
    }
]


@router.get("/samples")
def get_sample_templates():
    """Retrieve pre-built job description and resume templates."""
    return {
        "job_templates": [
            {
                "title": "Senior Full-Stack AI Engineer",
                "company": "NextGen AI Corp",
                "text": SAMPLE_JD_SENIOR_AI_FULLSTACK.strip()
            },
            {
                "title": "Senior Python Backend Engineer",
                "company": "ScaleCloud Systems",
                "text": SAMPLE_JD_BACKEND_PYTHON.strip()
            }
        ],
        "sample_resumes": [
            {"filename": r["filename"], "preview": r["text"][:200] + "..."}
            for r in SAMPLE_RESUMES_DATA
        ]
    }


@router.post("/seed", status_code=status.HTTP_201_CREATED)
async def seed_demo_scenario(db: Session = Depends(get_db)):
    """
    1-Click Demo Setup:
    Creates Senior Full-Stack AI Engineer JD, parses 5 diverse resumes (Senior AI, Backend Python,
    Junior Frontend, Data Analyst, Edge Case), screens and ranks them all immediately.
    """
    # 1. Create Job
    job = ScreenerService.create_or_parse_job(
        db=db,
        raw_text=SAMPLE_JD_SENIOR_AI_FULLSTACK.strip(),
        title="Senior Full-Stack AI Engineer",
        company="NextGen AI Corp"
    )

    # 2. Process all sample resumes
    created_resumes = []
    for s in SAMPLE_RESUMES_DATA:
        raw_bytes = s["text"].strip().encode("utf-8")
        resume = ScreenerService.process_and_save_resume(
            db=db,
            job_id=job.id,
            filename=s["filename"],
            file_bytes=raw_bytes
        )
        created_resumes.append(resume)

    # 3. Screen all candidates
    analyses = await ScreenerService.screen_all_resumes_for_job(db, job.id)
    
    # 4. Get ranked results
    ranked = ScreenerService.recalculate_ranks_for_job(db, job.id)

    return {
        "message": "Demo scenario successfully initialized and screened!",
        "job_id": job.id,
        "job_title": job.title,
        "total_screened": len(analyses),
        "top_candidate": ranked[0].name if ranked else None,
        "top_score": ranked[0].overall_score if ranked else 0.0,
        "ranked_candidates": [r.model_dump() for r in ranked]
    }
