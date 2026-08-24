import io
import pytest


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "llm_model" in data


def test_create_job_endpoint(client, sample_jd_text):
    payload = {
        "title": "Senior AI Engineer",
        "company": "Tech Corp",
        "raw_text": sample_jd_text
    }
    response = client.post("/api/jobs", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Senior AI Engineer"
    assert "structured_requirements" in data
    assert "Python" in data["structured_requirements"]["required_skills"]


def test_upload_resume_endpoint(client):
    file_content = b"Alex Chen\nSenior Engineer\nSkills: Python, FastAPI\nExperience: 5 years"
    files = [
        ("files", ("alex_chen.txt", io.BytesIO(file_content), "text/plain"))
    ]
    response = client.post("/api/resumes/upload", files=files)
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 1
    assert data[0]["filename"] == "alex_chen.txt"
    assert data[0]["status"] == "parsed"
    assert data[0]["candidate_name"] == "Alex Chen"


def test_end_to_end_screening_flow(client, sample_jd_text, sample_strong_resume_text):
    # 1. Create Job
    job_resp = client.post("/api/jobs", json={"title": "AI Engineer", "raw_text": sample_jd_text})
    assert job_resp.status_code == 201
    job_id = job_resp.json()["id"]

    # 2. Upload Resume
    files = [("files", ("alex.txt", io.BytesIO(sample_strong_resume_text.encode("utf-8")), "text/plain"))]
    upload_resp = client.post(f"/api/resumes/upload?job_id={job_id}", files=files, data={"job_id": job_id})
    assert upload_resp.status_code == 201
    resume_id = upload_resp.json()[0]["id"]
    candidate_id = upload_resp.json()[0]["candidate_id"]

    # 3. Screen
    screen_resp = client.post("/api/screen", json={"job_id": job_id})
    assert screen_resp.status_code == 200
    analyses = screen_resp.json()
    assert len(analyses) >= 1
    assert analyses[0]["overall_score"] >= 7.0

    # 4. Get Job Results
    results_resp = client.get(f"/api/jobs/{job_id}/results")
    assert results_resp.status_code == 200
    res_data = results_resp.json()
    assert res_data["total_resumes"] >= 1
    assert len(res_data["ranked_candidates"]) >= 1
    assert res_data["ranked_candidates"][0]["rank"] == 1


def test_demo_seed_endpoint(client):
    response = client.post("/api/demo/seed")
    assert response.status_code == 201
    data = response.json()
    assert data["total_screened"] == 5
    assert len(data["ranked_candidates"]) == 5
    # Rank #1 candidate should have the highest score
    assert data["ranked_candidates"][0]["overall_score"] >= data["ranked_candidates"][1]["overall_score"]
