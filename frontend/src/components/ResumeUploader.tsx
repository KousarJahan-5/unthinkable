import React, { useRef, useState } from 'react';
import { UploadCloud, File, CheckCircle2, AlertCircle, Trash2, Zap, RefreshCw } from 'lucide-react';
import type { ResumeUploadResponse } from '../types';

interface ResumeUploaderProps {
  uploadedResumes: ResumeUploadResponse[];
  onUpload: (files: File[]) => Promise<void>;
  onScreen: () => Promise<void>;
  onClearResumes: () => void;
  isUploading: boolean;
  isScreening: boolean;
  jobId: number | null;
}

export const ResumeUploader: React.FC<ResumeUploaderProps> = ({
  uploadedResumes,
  onUpload,
  onScreen,
  onClearResumes,
  isUploading,
  isScreening,
  jobId,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const filesArray = Array.from(e.dataTransfer.files);
      onUpload(filesArray);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const filesArray = Array.from(e.target.files);
      onUpload(filesArray);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6 shadow-xl backdrop-blur-md">
      <div className="flex items-center justify-between pb-4 border-b border-slate-700/60">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
            <UploadCloud className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white tracking-tight">Upload Resumes</h2>
            <p className="text-xs text-slate-400">Upload candidate CVs in PDF or text format</p>
          </div>
        </div>

        {uploadedResumes.length > 0 && (
          <button
            onClick={onClearResumes}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-700/50 hover:bg-rose-500/20 text-xs font-medium text-slate-300 hover:text-rose-300 border border-slate-600/50 transition-colors"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Reset List</span>
          </button>
        )}
      </div>

      {/* Drag & Drop Box */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`mt-4 border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all duration-200 ${
          isDragOver
            ? 'border-blue-500 bg-blue-500/10'
            : 'border-slate-700 hover:border-slate-600 bg-slate-900/40'
        }`}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          multiple
          accept=".pdf,.txt,.docx,.md"
          className="hidden"
        />

        <div className="flex flex-col items-center justify-center gap-2">
          <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center shadow-inner">
            <UploadCloud className="w-6 h-6 text-blue-400" />
          </div>
          <div className="text-sm font-semibold text-white">
            {isUploading ? 'Extracting text & parsing profiles...' : 'Click to browse or drop resumes here'}
          </div>
          <p className="text-xs text-slate-400">
            Supports multi-page <strong className="text-slate-300">PDF</strong>, <strong className="text-slate-300">TXT</strong>, and Markdown files (up to 10MB each)
          </p>
        </div>
      </div>

      {/* Uploaded File List */}
      {uploadedResumes.length > 0 && (
        <div className="mt-4 space-y-2 max-h-48 overflow-y-auto pr-1">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider px-1">
            Uploaded Files ({uploadedResumes.length})
          </div>
          {uploadedResumes.map((res) => {
            const isSuccess = res.status === 'parsed' || res.status === 'screened';
            return (
              <div
                key={res.id}
                className="flex items-center justify-between p-2.5 rounded-lg bg-slate-900/70 border border-slate-700/50 text-xs"
              >
                <div className="flex items-center gap-2.5 truncate">
                  <File className="w-4 h-4 text-slate-400 flex-shrink-0" />
                  <div className="truncate">
                    <span className="font-medium text-slate-200 truncate block">{res.filename}</span>
                    {res.candidate_name && (
                      <span className="text-[11px] text-blue-400">Candidate: {res.candidate_name}</span>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2 flex-shrink-0">
                  {isSuccess ? (
                    <span className="flex items-center gap-1 text-[11px] font-medium text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                      <CheckCircle2 className="w-3 h-3" />
                      {res.status === 'screened' ? 'Screened' : 'Parsed'}
                    </span>
                  ) : (
                    <span
                      className="flex items-center gap-1 text-[11px] font-medium text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20"
                      title={res.error_message || 'Error'}
                    >
                      <AlertCircle className="w-3 h-3" />
                      Failed
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Screening Execution CTA */}
      <div className="mt-5 pt-4 border-t border-slate-700/60 flex items-center justify-between">
        <div className="text-xs text-slate-400">
          {!jobId ? (
            <span className="text-amber-400">Please save a Job Description first</span>
          ) : uploadedResumes.length === 0 ? (
            <span>Upload at least 1 resume to begin screening</span>
          ) : (
            <span>{uploadedResumes.length} resume(s) ready for semantic matching</span>
          )}
        </div>

        <button
          onClick={onScreen}
          disabled={!jobId || uploadedResumes.length === 0 || isScreening || isUploading}
          className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-bold rounded-lg shadow-lg shadow-emerald-600/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isScreening ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Analyzing Candidates...</span>
            </>
          ) : (
            <>
              <Zap className="w-4 h-4" />
              <span>Screen & Rank Candidates</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};
