import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.job import Job
from app.models.resume import Resume
from app.models.candidate import Candidate
from app.models.analysis import CandidateAnalysis
from app.services.pdf_parser import PDFParser, PDFParsingError
from app.services.resume_extractor import ResumeExtractor
from app.services.jd_parser import JDParser
from app.services.llm_service import LLMService
from app.services.scoring_engine import ScoringEngine
from app.schemas.candidate import CandidateRankItem

logger = logging.getLogger(__name__)


class ScreenerService:
    """Orchestrator for end-to-end resume screening, ranking, and database persistence."""

    @classmethod
    def create_or_parse_job(cls, db: Session, raw_text: str, title: Optional[str] = None, company: Optional[str] = None) -> Job:
        """Parse raw JD text, extract requirements, and persist Job model."""
        structured = JDParser.parse(raw_text, default_title=title)
        
        job = Job(
            title=structured.get("title", title or "Software Position"),
            company=company or "",
            raw_text=raw_text,
            structured_requirements=structured
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @classmethod
    def process_and_save_resume(
        cls,
        db: Session,
        job_id: Optional[int],
        filename: str,
        file_bytes: bytes,
        file_path: Optional[str] = None
    ) -> Resume:
        """Parse resume file bytes, extract candidate profile, and create DB records."""
        resume = Resume(
            job_id=job_id,
            filename=filename,
            file_path=file_path,
            file_size=len(file_bytes),
            file_type=filename.split(".")[-1].lower() if "." in filename else "pdf",
            status="uploaded"
        )
        db.add(resume)
        db.flush()

        try:
            cleaned_text, meta = PDFParser.extract_text_from_bytes(file_bytes, filename)
            resume.raw_text = cleaned_text
            resume.cleaned_text = cleaned_text
            
            # Extract structured candidate profile
            candidate_dict = ResumeExtractor.extract(cleaned_text, filename)
            resume.parsed_data = candidate_dict
            resume.status = "parsed"

            # Create Candidate record
            candidate = Candidate(
                resume_id=resume.id,
                job_id=job_id,
                name=candidate_dict.get("name", "Unknown Candidate"),
                email=candidate_dict.get("email"),
                phone=candidate_dict.get("phone"),
                location=candidate_dict.get("location"),
                skills=candidate_dict.get("skills", []),
                technical_skills=candidate_dict.get("technical_skills", []),
                experience=candidate_dict.get("experience", []),
                education=candidate_dict.get("education", []),
                projects=candidate_dict.get("projects", []),
                certifications=candidate_dict.get("certifications", []),
                total_years_experience=candidate_dict.get("total_years_experience", 0)
            )
            db.add(candidate)
            db.commit()
            db.refresh(resume)
            return resume

        except PDFParsingError as pe:
            resume.status = "error"
            resume.error_message = str(pe)
            db.commit()
            db.refresh(resume)
            return resume
        except Exception as e:
            logger.error(f"Unexpected error processing resume {filename}: {str(e)}")
            resume.status = "error"
            resume.error_message = f"Failed to process resume: {str(e)}"
            db.commit()
            db.refresh(resume)
            return resume

    @classmethod
    async def screen_candidate(cls, db: Session, candidate_id: int, job_id: int) -> Optional[CandidateAnalysis]:
        """Screen an individual candidate against a specific Job Description."""
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        job = db.query(Job).filter(Job.id == job_id).first()

        if not candidate or not job:
            return None

        # Build candidate dictionary
        cand_data = {
            "name": candidate.name,
            "email": candidate.email,
            "phone": candidate.phone,
            "location": candidate.location,
            "skills": candidate.skills or [],
            "technical_skills": candidate.technical_skills or [],
            "experience": candidate.experience or [],
            "education": candidate.education or [],
            "projects": candidate.projects or [],
            "certifications": candidate.certifications or [],
            "total_years_experience": candidate.total_years_experience or 0
        }

        # 1. Run LLM evaluation (with fallback)
        llm_out, mode = await LLMService.analyze_candidate(
            candidate_data=cand_data,
            jd_requirements=job.structured_requirements or {},
            raw_resume_text=candidate.resume.cleaned_text if candidate.resume else "",
            raw_jd_text=job.raw_text
        )

        # 2. Run normalized scoring engine
        final_analysis = ScoringEngine.calculate_score(
            candidate_data=cand_data,
            jd_requirements=job.structured_requirements or {},
            llm_analysis=llm_out
        )

        # 3. Create or update CandidateAnalysis
        existing_analysis = db.query(CandidateAnalysis).filter(CandidateAnalysis.candidate_id == candidate.id).first()
        if existing_analysis:
            analysis = existing_analysis
        else:
            analysis = CandidateAnalysis(candidate_id=candidate.id, job_id=job.id)

        analysis.overall_score = final_analysis.overall_score
        analysis.recommendation = final_analysis.recommendation
        analysis.is_shortlisted = final_analysis.overall_score >= 7.0
        analysis.skills_match = final_analysis.skills_match.model_dump()
        analysis.experience_match = final_analysis.experience_match.model_dump()
        analysis.education_match = final_analysis.education_match.model_dump()
        analysis.relevant_projects = final_analysis.relevant_projects
        analysis.strengths = final_analysis.strengths
        analysis.gaps = final_analysis.gaps
        analysis.justification = final_analysis.justification
        analysis.raw_llm_response = llm_out.model_dump() if llm_out else None
        analysis.evaluation_mode = mode

        if candidate.resume:
            candidate.resume.status = "screened"

        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return analysis

    @classmethod
    async def screen_all_resumes_for_job(cls, db: Session, job_id: int) -> List[CandidateAnalysis]:
        """Screen all candidates assigned to a job and rank them."""
        candidates = db.query(Candidate).filter(Candidate.job_id == job_id).all()
        analyses = []
        for cand in candidates:
            res = await cls.screen_candidate(db, cand.id, job_id)
            if res:
                analyses.append(res)

        # Update ranks
        cls.recalculate_ranks_for_job(db, job_id)
        return analyses

    @classmethod
    def recalculate_ranks_for_job(cls, db: Session, job_id: int) -> List[CandidateRankItem]:
        """Rank all analyzed candidates for a job in descending score order."""
        analyses = db.query(CandidateAnalysis).filter(CandidateAnalysis.job_id == job_id).order_by(
            CandidateAnalysis.overall_score.desc()
        ).all()

        rank_items: List[CandidateRankItem] = []
        for idx, item in enumerate(analyses, start=1):
            item.rank = idx
            db.add(item)
            
            cand = item.candidate
            skills = item.skills_match or {}
            
            rank_items.append(CandidateRankItem(
                rank=idx,
                candidate_id=cand.id if cand else 0,
                resume_id=cand.resume_id if cand else 0,
                name=cand.name if cand else "Unknown",
                email=cand.email if cand else None,
                overall_score=item.overall_score,
                recommendation=item.recommendation,
                is_shortlisted=item.is_shortlisted,
                key_strength=item.strengths[0] if item.strengths else "Solid background",
                major_gap=item.gaps[0] if item.gaps else "None",
                total_years_experience=cand.total_years_experience if cand else 0,
                matched_skills_count=len(skills.get("matched", [])),
                missing_skills_count=len(skills.get("missing", []))
            ))

        db.commit()
        return rank_items
