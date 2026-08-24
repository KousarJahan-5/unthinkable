export interface StructuredRequirements {
  title: string;
  required_skills: string[];
  preferred_skills: string[];
  min_years_experience: number;
  education_requirements: string[];
  responsibilities: string[];
  domain_requirements: string[];
  location_requirements?: string;
}

export interface Job {
  id: number;
  title: string;
  company?: string;
  raw_text: string;
  structured_requirements: StructuredRequirements;
  created_at: string;
  updated_at: string;
  resume_count: number;
  candidate_count: number;
}

export interface SkillsMatch {
  matched: string[];
  partial: string[];
  missing: string[];
}

export interface SubMatchScore {
  score: number;
  summary: string;
}

export interface CandidateAnalysis {
  id: number;
  candidate_id: number;
  job_id: number;
  overall_score: number;
  recommendation: 'Strong Match' | 'Match' | 'Partial Match' | 'Weak Match';
  is_shortlisted: boolean;
  rank?: number;
  skills_match: SkillsMatch;
  experience_match: SubMatchScore;
  education_match: SubMatchScore;
  relevant_projects: (string | { name: string; description?: string })[];
  strengths: string[];
  gaps: string[];
  justification: string;
  evaluation_mode: string;
  created_at: string;
}

export interface Candidate {
  id: number;
  resume_id: number;
  job_id?: number;
  name: string;
  email?: string;
  phone?: string;
  location?: string;
  skills: string[];
  technical_skills: string[];
  experience: {
    title?: string;
    company?: string;
    duration?: string;
    years?: number;
    description?: string;
  }[];
  total_years_experience: number;
  education: {
    degree?: string;
    institution?: string;
    year?: string;
    field_of_study?: string;
  }[];
  projects: {
    name?: string;
    description?: string;
    technologies: string[];
  }[];
  certifications: string[];
  created_at: string;
  analysis?: CandidateAnalysis;
}

export interface CandidateRankItem {
  rank: number;
  candidate_id: number;
  resume_id: number;
  name: string;
  email?: string;
  overall_score: number;
  recommendation: 'Strong Match' | 'Match' | 'Partial Match' | 'Weak Match';
  is_shortlisted: boolean;
  key_strength: string;
  major_gap: string;
  total_years_experience: number;
  matched_skills_count: number;
  missing_skills_count: number;
}

export interface JobScreeningResults {
  job_id: number;
  job_title: string;
  total_resumes: number;
  total_processed: number;
  total_shortlisted: number;
  average_score: number;
  ranked_candidates: CandidateRankItem[];
  score_distribution: {
    'Strong Match': number;
    'Match': number;
    'Partial Match': number;
    'Weak Match': number;
  };
}

export interface ResumeUploadResponse {
  id: number;
  job_id?: number;
  filename: string;
  file_size: number;
  file_type: string;
  status: string;
  error_message?: string;
  created_at: string;
  candidate_id?: number;
  candidate_name?: string;
}

export interface HealthStatus {
  status: string;
  app_name: string;
  environment: string;
  llm_provider: string;
  llm_configured: boolean;
  llm_model: string;
  evaluation_mode: string;
}
