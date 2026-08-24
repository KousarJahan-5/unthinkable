import React, { useState } from 'react';
import { Trophy, Star, Eye, ArrowUpDown } from 'lucide-react';
import type { CandidateRankItem } from '../types';
import { ScoreBadge } from './ScoreBadge';

interface CandidateRankingTableProps {
  candidates: CandidateRankItem[];
  onSelectCandidate: (candidateId: number) => void;
  isLoading: boolean;
}

export const CandidateRankingTable: React.FC<CandidateRankingTableProps> = ({
  candidates,
  onSelectCandidate,
  isLoading,
}) => {
  const [filterRecommendation, setFilterRecommendation] = useState<string>('ALL');
  const [onlyShortlisted, setOnlyShortlisted] = useState(false);
  const [sortOrder, setSortOrder] = useState<'desc' | 'asc'>('desc');

  // Filter candidates
  const filteredCandidates = candidates.filter((c) => {
    if (onlyShortlisted && !c.is_shortlisted) return false;
    if (filterRecommendation !== 'ALL' && c.recommendation !== filterRecommendation) return false;
    return true;
  });

  // Sort candidates
  const sortedCandidates = [...filteredCandidates].sort((a, b) => {
    return sortOrder === 'desc' ? b.overall_score - a.overall_score : a.overall_score - b.overall_score;
  });

  const getRecommendationBadge = (rec: string) => {
    switch (rec) {
      case 'Strong Match':
        return 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30';
      case 'Match':
        return 'bg-blue-500/15 text-blue-300 border-blue-500/30';
      case 'Partial Match':
        return 'bg-amber-500/15 text-amber-300 border-amber-500/30';
      default:
        return 'bg-rose-500/15 text-rose-300 border-rose-500/30';
    }
  };

  const getRankBadge = (rank: number) => {
    if (rank === 1) {
      return (
        <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-gradient-to-tr from-amber-400 to-yellow-300 text-slate-950 font-black text-xs shadow-md shadow-amber-400/30">
          #1
        </span>
      );
    } else if (rank === 2) {
      return (
        <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-gradient-to-tr from-slate-300 to-slate-200 text-slate-950 font-black text-xs shadow-md">
          #2
        </span>
      );
    } else if (rank === 3) {
      return (
        <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-gradient-to-tr from-amber-600 to-amber-500 text-white font-black text-xs shadow-md">
          #3
        </span>
      );
    }
    return (
      <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-slate-800 text-slate-400 font-bold text-xs border border-slate-700">
        #{rank}
      </span>
    );
  };

  return (
    <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl shadow-xl backdrop-blur-md overflow-hidden">
      {/* Header & Filter Controls */}
      <div className="p-6 border-b border-slate-700/60 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
            <Trophy className="w-5 h-5 text-indigo-400" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white tracking-tight">Candidate Ranking Leaderboard</h2>
            <p className="text-xs text-slate-400">
              Ranked candidates based on semantic suitability, skills alignment, and relevant experience
            </p>
          </div>
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="inline-flex rounded-lg bg-slate-900/80 p-1 border border-slate-700 text-xs">
            {['ALL', 'Strong Match', 'Match', 'Partial Match', 'Weak Match'].map((tab) => (
              <button
                key={tab}
                onClick={() => setFilterRecommendation(tab)}
                className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                  filterRecommendation === tab
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {tab === 'ALL' ? 'All Candidates' : tab}
              </button>
            ))}
          </div>

          <button
            onClick={() => setOnlyShortlisted(!onlyShortlisted)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
              onlyShortlisted
                ? 'bg-amber-500/20 text-amber-300 border-amber-500/40 shadow-sm'
                : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-slate-200'
            }`}
          >
            <Star className={`w-3.5 h-3.5 ${onlyShortlisted ? 'fill-amber-400 text-amber-400' : ''}`} />
            <span>Shortlisted Only</span>
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-900/90 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-700">
            <tr>
              <th className="py-3.5 px-4 w-16 text-center">Rank</th>
              <th className="py-3.5 px-4">Candidate</th>
              <th
                className="py-3.5 px-4 cursor-pointer select-none hover:text-white"
                onClick={() => setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc')}
              >
                <div className="flex items-center gap-1">
                  <span>Match Score</span>
                  <ArrowUpDown className="w-3.5 h-3.5" />
                </div>
              </th>
              <th className="py-3.5 px-4">Recommendation</th>
              <th className="py-3.5 px-4">Key Strength</th>
              <th className="py-3.5 px-4">Major Gap</th>
              <th className="py-3.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700/50 text-slate-200">
            {isLoading ? (
              <tr>
                <td colSpan={7} className="py-12 text-center text-slate-400">
                  <div className="inline-block animate-spin w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full mb-2" />
                  <p>Processing candidates & calculating semantic scores...</p>
                </td>
              </tr>
            ) : sortedCandidates.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-12 text-center text-slate-400">
                  <p className="text-sm font-medium text-slate-300">No candidates match the selected filters.</p>
                  <p className="text-xs text-slate-500 mt-1">Upload resumes and click "Screen Candidates" to see rankings.</p>
                </td>
              </tr>
            ) : (
              sortedCandidates.map((candidate) => (
                <tr
                  key={candidate.candidate_id}
                  onClick={() => onSelectCandidate(candidate.candidate_id)}
                  className="hover:bg-slate-700/30 transition-colors cursor-pointer group"
                >
                  {/* Rank */}
                  <td className="py-3.5 px-4 text-center">
                    <div className="flex items-center justify-center">
                      {getRankBadge(candidate.rank)}
                    </div>
                  </td>

                  {/* Candidate Profile */}
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-2.5">
                      <div>
                        <div className="font-bold text-white text-sm group-hover:text-blue-400 transition-colors flex items-center gap-1.5">
                          <span>{candidate.name}</span>
                          {candidate.is_shortlisted && (
                            <span title="Shortlisted">
                              <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
                            </span>
                          )}
                        </div>
                        <div className="text-[11px] text-slate-400">
                          {candidate.email || 'No email provided'} • {candidate.total_years_experience || 0} yrs exp
                        </div>
                      </div>
                    </div>
                  </td>

                  {/* Score */}
                  <td className="py-3.5 px-4">
                    <ScoreBadge score={candidate.overall_score} />
                  </td>

                  {/* Recommendation */}
                  <td className="py-3.5 px-4">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${getRecommendationBadge(
                        candidate.recommendation
                      )}`}
                    >
                      {candidate.recommendation}
                    </span>
                  </td>

                  {/* Key Strength */}
                  <td className="py-3.5 px-4 max-w-xs truncate text-slate-300" title={candidate.key_strength}>
                    <span className="text-emerald-400 mr-1">✓</span> {candidate.key_strength}
                  </td>

                  {/* Major Gap */}
                  <td className="py-3.5 px-4 max-w-xs truncate text-slate-400" title={candidate.major_gap}>
                    <span className="text-rose-400 mr-1">✗</span> {candidate.major_gap}
                  </td>

                  {/* Action */}
                  <td className="py-3.5 px-4 text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectCandidate(candidate.candidate_id);
                      }}
                      className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-blue-600/20 hover:bg-blue-600 text-blue-300 hover:text-white border border-blue-500/30 text-xs font-medium transition-all"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      <span>Inspect</span>
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
