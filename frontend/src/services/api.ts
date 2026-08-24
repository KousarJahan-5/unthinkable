import axios from 'axios';
import type {
  Job,
  JobScreeningResults,
  Candidate,
  CandidateAnalysis,
  ResumeUploadResponse,
  HealthStatus,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Health
  getHealth: async (): Promise<HealthStatus> => {
    const res = await client.get<HealthStatus>('/api/health');
    return res.data;
  },

  // Jobs
  createJob: async (data: { title?: string; company?: string; raw_text: string }): Promise<Job> => {
    const res = await client.post<Job>('/api/jobs', data);
    return res.data;
  },

  listJobs: async (): Promise<Job[]> => {
    const res = await client.get<Job[]>('/api/jobs');
    return res.data;
  },

  getJob: async (id: number): Promise<Job> => {
    const res = await client.get<Job>(`/api/jobs/${id}`);
    return res.data;
  },

  // Resumes
  uploadResumes: async (files: File[], jobId?: number): Promise<ResumeUploadResponse[]> => {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });
    if (jobId) {
      formData.append('job_id', jobId.toString());
    }

    const res = await client.post<ResumeUploadResponse[]>('/api/resumes/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },

  // Screening & Results
  screenJob: async (jobId: number, candidateIds?: number[]): Promise<CandidateAnalysis[]> => {
    const res = await client.post<CandidateAnalysis[]>('/api/screen', {
      job_id: jobId,
      candidate_ids: candidateIds,
    });
    return res.data;
  },

  getJobResults: async (jobId: number): Promise<JobScreeningResults> => {
    const res = await client.get<JobScreeningResults>(`/api/jobs/${jobId}/results`);
    return res.data;
  },

  // Candidates
  listCandidates: async (jobId?: number, isShortlisted?: boolean): Promise<Candidate[]> => {
    const params = new URLSearchParams();
    if (jobId !== undefined) params.append('job_id', jobId.toString());
    if (isShortlisted !== undefined) params.append('is_shortlisted', isShortlisted.toString());

    const res = await client.get<Candidate[]>(`/api/candidates?${params.toString()}`);
    return res.data;
  },

  getCandidate: async (id: number): Promise<Candidate> => {
    const res = await client.get<Candidate>(`/api/candidates/${id}`);
    return res.data;
  },

  // Demo Seeding
  seedDemo: async (): Promise<{
    message: string;
    job_id: number;
    job_title: string;
    total_screened: number;
    top_candidate: string;
    top_score: number;
  }> => {
    const res = await client.post('/api/demo/seed');
    return res.data;
  },

  getSampleTemplates: async (): Promise<{
    job_templates: { title: string; company: string; text: string }[];
    sample_resumes: { filename: string; preview: string }[];
  }> => {
    const res = await client.get('/api/demo/samples');
    return res.data;
  },
};
