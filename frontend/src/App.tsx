import React, { useState, useEffect } from 'react';
import { api } from './services/api';
import type { Job, JobScreeningResults, Candidate, ResumeUploadResponse, HealthStatus } from './types';
import { Navbar } from './components/Navbar';
import { MetricCards } from './components/MetricCards';
import { JobDescriptionInput } from './components/JobDescriptionInput';
import { ResumeUploader } from './components/ResumeUploader';
import { CandidateRankingTable } from './components/CandidateRankingTable';
import { CandidateDetailModal } from './components/CandidateDetailModal';
import { CheckCircle2, AlertCircle, Info } from 'lucide-react';

export const App: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [currentJob, setCurrentJob] = useState<Job | null>(null);
  const [uploadedResumes, setUploadedResumes] = useState<ResumeUploadResponse[]>([]);
  const [screeningResults, setScreeningResults] = useState<JobScreeningResults | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);
  const [sampleTemplates, setSampleTemplates] = useState<{ title: string; company: string; text: string }[]>([]);

  // Loading states
  const [isLoadingJob, setIsLoadingJob] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isScreening, setIsScreening] = useState(false);
  const [isSeeding, setIsSeeding] = useState(false);

  // Notification / Alert Banner
  const [notification, setNotification] = useState<{
    type: 'success' | 'error' | 'info';
    message: string;
  } | null>(null);

  const showNotification = (type: 'success' | 'error' | 'info', message: string) => {
    setNotification({ type, message });
    setTimeout(() => {
      setNotification((prev) => (prev?.message === message ? null : prev));
    }, 5000);
  };

  // Initial Load
  useEffect(() => {
    const initData = async () => {
      try {
        const h = await api.getHealth();
        setHealth(h);
      } catch (err) {
        console.error('Failed to fetch health:', err);
      }

      try {
        const samples = await api.getSampleTemplates();
        setSampleTemplates(samples.job_templates || []);
      } catch (err) {
        console.error('Failed to fetch sample templates:', err);
      }
    };
    initData();
  }, []);

  // Save/Parse Job Description
  const handleSaveJob = async (title: string, company: string, text: string) => {
    setIsLoadingJob(true);
    try {
      const job = await api.createJob({ title, company, raw_text: text });
      setCurrentJob(job);
      showNotification('success', `Job "${job.title}" created & requirements parsed successfully!`);
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to save job description.';
      showNotification('error', msg);
    } finally {
      setIsLoadingJob(false);
    }
  };

  // Upload Resumes
  const handleUploadResumes = async (files: File[]) => {
    setIsUploading(true);
    try {
      const responses = await api.uploadResumes(files, currentJob?.id);
      setUploadedResumes((prev) => [...prev, ...responses]);
      showNotification(
        'success',
        `Successfully uploaded and parsed ${responses.length} resume(s)!`
      );
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to upload resumes.';
      showNotification('error', msg);
    } finally {
      setIsUploading(false);
    }
  };

  // Screen Candidates
  const handleScreenCandidates = async () => {
    if (!currentJob) {
      showNotification('error', 'Please create or select a Job Description first.');
      return;
    }
    setIsScreening(true);
    try {
      await api.screenJob(currentJob.id);
      const results = await api.getJobResults(currentJob.id);
      setScreeningResults(results);
      showNotification('success', `Screening complete! Ranked ${results.ranked_candidates.length} candidates.`);
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Screening failed. Please retry.';
      showNotification('error', msg);
    } finally {
      setIsScreening(false);
    }
  };

  // 1-Click Demo Seed
  const handleSeedDemo = async () => {
    setIsSeeding(true);
    try {
      const res = await api.seedDemo();
      // Fetch Job Details
      const job = await api.getJob(res.job_id);
      setCurrentJob(job);

      // Fetch Results
      const results = await api.getJobResults(res.job_id);
      setScreeningResults(results);

      // Populate uploaded resumes
      const candidates = await api.listCandidates(res.job_id);
      const mockUploads: ResumeUploadResponse[] = candidates.map((c) => ({
        id: c.resume_id,
        job_id: res.job_id,
        filename: `${c.name.replace(/\s+/g, '_')}_Resume.pdf`,
        file_size: 15420,
        file_type: 'pdf',
        status: 'screened',
        created_at: c.created_at,
        candidate_id: c.id,
        candidate_name: c.name,
      }));
      setUploadedResumes(mockUploads);

      showNotification(
        'success',
        `Demo scenario loaded! Screened 5 candidates for "${res.job_title}".`
      );
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to seed demo scenario.';
      showNotification('error', msg);
    } finally {
      setIsSeeding(false);
    }
  };

  // Inspect Candidate
  const handleSelectCandidate = async (candidateId: number) => {
    try {
      const candidate = await api.getCandidate(candidateId);
      setSelectedCandidate(candidate);
    } catch (err) {
      showNotification('error', 'Failed to fetch candidate details.');
    }
  };

  const handleClearResumes = () => {
    setUploadedResumes([]);
    setScreeningResults(null);
    showNotification('info', 'Resume list cleared.');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Navigation Header */}
      <Navbar health={health} onSeedDemo={handleSeedDemo} isSeeding={isSeeding} />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Notification Toast */}
        {notification && (
          <div
            className={`p-4 rounded-xl text-xs font-medium border flex items-center justify-between transition-all shadow-lg backdrop-blur-md ${
              notification.type === 'success'
                ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                : notification.type === 'error'
                ? 'bg-rose-500/15 text-rose-300 border-rose-500/30'
                : 'bg-blue-500/15 text-blue-300 border-blue-500/30'
            }`}
          >
            <div className="flex items-center gap-2.5">
              {notification.type === 'success' && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
              {notification.type === 'error' && <AlertCircle className="w-4 h-4 text-rose-400" />}
              {notification.type === 'info' && <Info className="w-4 h-4 text-blue-400" />}
              <span>{notification.message}</span>
            </div>
            <button
              onClick={() => setNotification(null)}
              className="text-slate-400 hover:text-white text-xs px-2 py-0.5"
            >
              ✕
            </button>
          </div>
        )}

        {/* Dashboard Metrics */}
        <MetricCards results={screeningResults} uploadedCount={uploadedResumes.length} />

        {/* Two-Column Workspace: JD and Resume Upload */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <JobDescriptionInput
            currentJob={currentJob}
            onSaveJob={handleSaveJob}
            isLoading={isLoadingJob}
            sampleTemplates={sampleTemplates}
          />
          <ResumeUploader
            uploadedResumes={uploadedResumes}
            onUpload={handleUploadResumes}
            onScreen={handleScreenCandidates}
            onClearResumes={handleClearResumes}
            isUploading={isUploading}
            isScreening={isScreening}
            jobId={currentJob?.id || null}
          />
        </div>

        {/* Candidate Ranking Leaderboard */}
        <CandidateRankingTable
          candidates={screeningResults?.ranked_candidates || []}
          onSelectCandidate={handleSelectCandidate}
          isLoading={isScreening}
        />
      </main>

      {/* Candidate Deep Inspection Modal */}
      <CandidateDetailModal
        candidate={selectedCandidate}
        onClose={() => setSelectedCandidate(null)}
      />

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-slate-900/50 py-6 text-center text-xs text-slate-500">
        <p>
          Smart Resume Screener • Production Full-Stack AI Architecture • Built with FastAPI, React & Semantic LLM Matching
        </p>
      </footer>
    </div>
  );
};

export default App;
