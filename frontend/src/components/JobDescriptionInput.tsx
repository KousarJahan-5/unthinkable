import React, { useState } from 'react';
import { Briefcase, FileText, CheckCircle2, ChevronDown, Sparkles, Building2 } from 'lucide-react';
import type { Job } from '../types';

interface JobDescriptionInputProps {
  currentJob: Job | null;
  onSaveJob: (title: string, company: string, text: string) => Promise<void>;
  isLoading: boolean;
  sampleTemplates?: { title: string; company: string; text: string }[];
}

export const JobDescriptionInput: React.FC<JobDescriptionInputProps> = ({
  currentJob,
  onSaveJob,
  isLoading,
  sampleTemplates = [],
}) => {
  const [title, setTitle] = useState(currentJob?.title || '');
  const [company, setCompany] = useState(currentJob?.company || '');
  const [text, setText] = useState(currentJob?.raw_text || '');
  const [showPresets, setShowPresets] = useState(false);

  const handleSelectPreset = (preset: { title: string; company: string; text: string }) => {
    setTitle(preset.title);
    setCompany(preset.company);
    setText(preset.text);
    setShowPresets(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    await onSaveJob(title, company, text);
  };

  return (
    <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6 shadow-xl backdrop-blur-md">
      <div className="flex items-center justify-between pb-4 border-b border-slate-700/60">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
            <Briefcase className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white tracking-tight">Job Description (JD)</h2>
            <p className="text-xs text-slate-400">Define requirements to semantically evaluate applicants</p>
          </div>
        </div>

        {/* Preset Selector */}
        {sampleTemplates.length > 0 && (
          <div className="relative">
            <button
              type="button"
              onClick={() => setShowPresets(!showPresets)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-700/50 hover:bg-slate-700 text-xs font-medium text-slate-200 border border-slate-600/50 transition-colors"
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span>Load Template</span>
              <ChevronDown className="w-3 h-3 text-slate-400" />
            </button>

            {showPresets && (
              <div className="absolute right-0 mt-2 w-64 rounded-xl bg-slate-800 border border-slate-700 shadow-2xl z-50 py-1 overflow-hidden">
                <div className="px-3 py-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-700/50">
                  Pre-Configured Roles
                </div>
                {sampleTemplates.map((template, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleSelectPreset(template)}
                    className="w-full text-left px-3 py-2 text-xs text-slate-200 hover:bg-slate-700/60 transition-colors flex flex-col"
                  >
                    <span className="font-semibold text-white">{template.title}</span>
                    <span className="text-[11px] text-slate-400">{template.company}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="mt-4 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Position Title</label>
            <div className="relative">
              <FileText className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="e.g. Senior Full-Stack AI Engineer"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full pl-9 pr-3 py-2 bg-slate-900/80 border border-slate-700 rounded-lg text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Company / Department</label>
            <div className="relative">
              <Building2 className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="e.g. NextGen AI Corp"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                className="w-full pl-9 pr-3 py-2 bg-slate-900/80 border border-slate-700 rounded-lg text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1">
            Job Description & Qualifications <span className="text-rose-400">*</span>
          </label>
          <textarea
            rows={6}
            placeholder="Paste complete Job Description including required skills, years of experience, responsibilities, and preferred qualifications..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            required
            className="w-full p-3 bg-slate-900/80 border border-slate-700 rounded-lg text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 font-mono leading-relaxed"
          />
        </div>

        <div className="flex items-center justify-between">
          <span className="text-[11px] text-slate-400">
            {text.length > 0 ? `${text.split(/\s+/).filter(Boolean).length} words entered` : 'Minimum 15 characters required'}
          </span>
          <button
            type="submit"
            disabled={isLoading || !text.trim() || text.length < 15}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg shadow-md shadow-blue-600/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <span>Parsing JD...</span>
            ) : (
              <>
                <CheckCircle2 className="w-4 h-4" />
                <span>{currentJob ? 'Update & Reparse JD' : 'Save & Parse Job Description'}</span>
              </>
            )}
          </button>
        </div>
      </form>

      {/* Extracted Structured Requirements Preview */}
      {currentJob?.structured_requirements && (
        <div className="mt-5 pt-4 border-t border-slate-700/60">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              Parsed Requirements (Active Job #{currentJob.id})
            </span>
            <span className="text-xs text-slate-400">
              Min Exp: <strong className="text-white">{currentJob.structured_requirements.min_years_experience || 0}+ yrs</strong>
            </span>
          </div>

          <div className="space-y-2 text-xs">
            {/* Required Skills */}
            {currentJob.structured_requirements.required_skills?.length > 0 && (
              <div className="flex flex-wrap items-center gap-1.5">
                <span className="text-[11px] font-semibold text-rose-400 bg-rose-500/10 border border-rose-500/20 px-2 py-0.5 rounded">
                  Mandatory Skills:
                </span>
                {currentJob.structured_requirements.required_skills.map((skill, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-0.5 rounded bg-slate-700/80 text-slate-200 border border-slate-600/50"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            )}

            {/* Preferred Skills */}
            {currentJob.structured_requirements.preferred_skills?.length > 0 && (
              <div className="flex flex-wrap items-center gap-1.5">
                <span className="text-[11px] font-semibold text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 px-2 py-0.5 rounded">
                  Preferred Skills:
                </span>
                {currentJob.structured_requirements.preferred_skills.map((skill, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-0.5 rounded bg-slate-700/80 text-slate-300 border border-slate-600/50"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
