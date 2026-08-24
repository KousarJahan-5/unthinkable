import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app

# In-memory SQLite for isolated automated tests with StaticPool
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh isolated database for each test."""
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient with overridden database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_jd_text():
    return """
Senior AI Engineer
Required Qualifications:
- 5+ years of experience with Python, FastAPI, and PostgreSQL.
- Strong practical experience with LLMs, RAG, and PyTorch.
- Experience with Docker and CI/CD.
- Bachelor's degree in Computer Science.

Preferred:
- Kubernetes (k8s) and AWS experience.
- Experience with React and TypeScript.
"""


@pytest.fixture
def sample_strong_resume_text():
    return """
Alex Chen
San Francisco, CA | alex@example.com | +1 (415) 555-0192

Summary:
Senior AI Engineer with 6 years of experience building Python and FastAPI microservices, LLMs, and RAG pipelines.

Skills:
Python, FastAPI, PostgreSQL, LLM, RAG, PyTorch, Docker, Kubernetes, React, TypeScript, AWS, CI/CD

Work Experience:
Senior AI Engineer | 2021 - Present
- Built GenAI services using FastAPI and PyTorch.
- Designed vector databases and RAG pipelines.

Education:
Master of Science in Computer Science | Stanford University (2018)
"""
