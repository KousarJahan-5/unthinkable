import React from 'react';
import {
  X,
  Mail,
  Phone,
  MapPin,
  Briefcase,
  GraduationCap,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Layers,
  Star,
  Quote,
} from 'lucide-react';
import type { Candidate } from '../types';

interface CandidateDetailModalProps {
  candidate: Candidate | null;
  onClose: () => void;
}

export const CandidateDetailModal: React.FC<CandidateDetailModalProps> = ({ candidate, onClose }) => {
  if (!candidate) return null;

  const analysis = candidate.analysis;
  const skillsMatch = analysis?.skills_match;

  const getRecommendationStyle = (rec?: string) => {
    switch (rec) {
      case 'Strong Match':
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
      case 'Match':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/40';
      case 'Partial Match':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      default:
        return 'bg-rose-500/20 text-rose-300 border-rose-500/40';
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-slate-950/80 backdrop-blur-md overflow-y-auto">
      <div className="relative w-full max-w-4xl max-h-[90vh] bg-slate-900 border border-slate-700/80 rounded-3xl shadow-2xl overflow-y-auto">
        {/* Modal Header */}
        <div className="sticky top-0 z-10 bg-slate-900/95 backdrop-blur-md border-b border-slate-800 p-6 flex items-start justify-between">
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-blue-500/20">
              {candidate.name.charAt(0)}
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-xl font-bold text-white tracking-tight">{candidate.name}</h1>
                {analysis?.is_shortlisted && (
                  <span className="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40">
                    <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
                    Shortlisted
                  </span>
                )}
              </div>

              {/* Contact meta */}
              <div className="flex flex-wrap items-center gap-4 mt-2 text-xs text-slate-400">
                {candidate.email && (
                  <div className="flex items-center gap-1.5">
                    <Mail className="w-3.5 h-3.5 text-slate-500" />
                    <span>{candidate.email}</span>
                  </div>
                )}
                {candidate.phone && (
                  <div className="flex items-center gap-1.5">
                    <Phone className="w-3.5 h-3.5 text-slate-500" />
                    <span>{candidate.phone}</span>
                  </div>
                )}
                {candidate.location && (
                  <div className="flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-slate-500" />
                    <span>{candidate.location}</span>
                  </div>
                )}
                <div className="flex items-center gap-1.5 text-slate-300 font-medium">
                  <Briefcase className="w-3.5 h-3.5 text-blue-400" />
                  <span>{candidate.total_years_experience || 0}+ Years Professional Exp</span>
                </div>
              </div>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-6">
          {/* Top Score Banner */}
          {analysis && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-slate-800/40 border border-slate-700/60 rounded-2xl p-5 backdrop-blur-sm">
              {/* Overall Score */}
              <div className="flex flex-col justify-center items-center md:border-r border-slate-700/60 p-2">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                  Overall Match Score
                </span>
                <div className="text-4xl font-extrabold text-white tracking-tight flex items-baseline gap-1">
                  <span className="text-blue-400">{analysis.overall_score.toFixed(1)}</span>
                  <span className="text-lg font-semibold text-slate-500">/ 10</span>
                </div>
                <span
                  className={`mt-2 px-3 py-0.5 rounded-full text-xs font-bold border ${getRecommendationStyle(
                    analysis.recommendation
                  )}`}
                >
                  {analysis.recommendation}
                </span>
              </div>

              {/* Sub-Score Bars */}
              <div className="md:col-span-2 space-y-3 justify-center flex flex-col px-2">
                {/* Experience Subscore */}
                <div>
                  <div className="flex justify-between text-xs font-medium mb-1">
                    <span className="text-slate-300">Relevant Experience (30%)</span>
                    <span className="text-white font-bold">{analysis.experience_match?.score ?? 0} / 10</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${((analysis.experience_match?.score ?? 0) / 10) * 100}%` }}
                    />
                  </div>
                </div>

                {/* Education Subscore */}
                <div>
                  <div className="flex justify-between text-xs font-medium mb-1">
                    <span className="text-slate-300">Academic & Education Alignment (10%)</span>
                    <span className="text-white font-bold">{analysis.education_match?.score ?? 0} / 10</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div
                      className="bg-purple-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${((analysis.education_match?.score ?? 0) / 10) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Justification Narrative */}
          {analysis?.justification && (
            <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20 text-xs leading-relaxed text-blue-200 flex items-start gap-3">
              <Quote className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
              <div>
                <span className="font-bold text-white block mb-1">Recruiter Justification:</span>
                <p>{analysis.justification}</p>
              </div>
            </div>
          )}

          {/* Skills Breakdown (Matched / Partial / Missing) */}
          <div className="bg-slate-800/40 border border-slate-700/60 rounded-2xl p-5 space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Layers className="w-4 h-4 text-blue-400" />
              <span>Skills & Technical Capabilities Breakdown</span>
            </h3>

            {/* Matched Skills */}
            <div>
              <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-400 mb-2">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Fully Matched Skills ({skillsMatch?.matched?.length || 0})</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {skillsMatch?.matched && skillsMatch.matched.length > 0 ? (
                  skillsMatch.matched.map((s, idx) => (
                    <span
                      key={idx}
                      className="px-2.5 py-1 rounded-lg bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 text-xs font-medium"
                    >
                      ✓ {s}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-slate-500 italic">No exact mandatory skills matched</span>
                )}
              </div>
            </div>

            {/* Partial Skills */}
            {skillsMatch?.partial && skillsMatch.partial.length > 0 && (
              <div>
                <div className="flex items-center gap-1.5 text-xs font-semibold text-amber-400 mb-2">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>Partial / Related Skills ({skillsMatch.partial.length})</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {skillsMatch.partial.map((s, idx) => (
                    <span
                      key={idx}
                      className="px-2.5 py-1 rounded-lg bg-amber-500/15 text-amber-300 border border-amber-500/30 text-xs font-medium"
                    >
                      ~ {s}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Missing Skills */}
            <div>
              <div className="flex items-center gap-1.5 text-xs font-semibold text-rose-400 mb-2">
                <XCircle className="w-3.5 h-3.5" />
                <span>Missing JD Requirements ({skillsMatch?.missing?.length || 0})</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {skillsMatch?.missing && skillsMatch.missing.length > 0 ? (
                  skillsMatch.missing.map((s, idx) => (
                    <span
                      key={idx}
                      className="px-2.5 py-1 rounded-lg bg-rose-500/15 text-rose-300 border border-rose-500/30 text-xs font-medium"
                    >
                      ✗ {s}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-emerald-400 italic">None — Meets all stated skill requirements!</span>
                )}
              </div>
            </div>
          </div>

          {/* Strengths & Gaps Two-Column Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Strengths */}
            <div className="bg-slate-800/40 border border-slate-700/60 rounded-2xl p-5">
              <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-2 mb-3">
                <CheckCircle2 className="w-4 h-4" />
                <span>Key Candidate Strengths</span>
              </h3>
              <ul className="space-y-2 text-xs text-slate-300">
                {analysis?.strengths && analysis.strengths.length > 0 ? (
                  analysis.strengths.map((st, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-emerald-400 font-bold">•</span>
                      <span>{st}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-slate-500 italic">No specific strengths recorded</li>
                )}
              </ul>
            </div>

            {/* Gaps */}
            <div className="bg-slate-800/40 border border-slate-700/60 rounded-2xl p-5">
              <h3 className="text-xs font-bold uppercase tracking-wider text-rose-400 flex items-center gap-2 mb-3">
                <AlertTriangle className="w-4 h-4" />
                <span>Skill & Experience Gaps</span>
              </h3>
              <ul className="space-y-2 text-xs text-slate-300">
                {analysis?.gaps && analysis.gaps.length > 0 ? (
                  analysis.gaps.map((gp, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-rose-400 font-bold">•</span>
                      <span>{gp}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-emerald-400 italic">No significant disqualifying gaps found</li>
                )}
              </ul>
            </div>
          </div>

          {/* Experience & Education Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Experience */}
            <div className="bg-slate-800/40 border border-slate-700/60 rounded-2xl p-5">
              <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400 flex items-center gap-2 mb-3">
                <Briefcase className="w-4 h-4" />
                <span>Work Experience & Roles</span>
              </h3>
              {candidate.experience && candidate.experience.length > 0 ? (
                <div className="space-y-3 text-xs">
                  {candidate.experience.map((exp, idx) => (
                    <div key={idx} className="border-l-2 border-slate-700 pl-3 py-1">
                      <div className="font-semibold text-white">{exp.title || 'Role'}</div>
                      <div className="text-[11px] text-slate-400">{exp.company || 'Company'} • {exp.duration || 'Past'}</div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-500 italic">No explicit roles parsed</p>
              )}
            </div>

            {/* Education */}
            <div className="bg-slate-800/40 border border-slate-700/60 rounded-2xl p-5">
              <h3 className="text-xs font-bold uppercase tracking-wider text-purple-400 flex items-center gap-2 mb-3">
                <GraduationCap className="w-4 h-4" />
                <span>Education & Credentials</span>
              </h3>
              {candidate.education && candidate.education.length > 0 ? (
                <div className="space-y-3 text-xs">
                  {candidate.education.map((edu, idx) => (
                    <div key={idx} className="border-l-2 border-slate-700 pl-3 py-1">
                      <div className="font-semibold text-white">{edu.degree || 'Degree'}</div>
                      <div className="text-[11px] text-slate-400">
                        {edu.institution || 'University'} {edu.year ? `(${edu.year})` : ''}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-500 italic">No formal degree credentials found</p>
              )}
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="sticky bottom-0 bg-slate-900/95 backdrop-blur-md border-t border-slate-800 p-4 flex items-center justify-between">
          <span className="text-xs text-slate-500">
            Evaluation Engine: <strong className="text-slate-300">{analysis?.evaluation_mode || 'Semantic AI'}</strong>
          </span>
          <button
            onClick={onClose}
            className="px-5 py-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold rounded-xl transition-colors"
          >
            Close Inspection
          </button>
        </div>
      </div>
    </div>
  );
};
