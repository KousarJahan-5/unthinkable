import React from 'react';
import { Users, CheckCircle2, Star, TrendingUp, Award } from 'lucide-react';
import type { JobScreeningResults } from '../types';

interface MetricCardsProps {
  results: JobScreeningResults | null;
  uploadedCount: number;
}

export const MetricCards: React.FC<MetricCardsProps> = ({ results, uploadedCount }) => {
  const totalResumes = results?.total_resumes ?? uploadedCount;
  const totalProcessed = results?.total_processed ?? 0;
  const totalShortlisted = results?.total_shortlisted ?? 0;
  const averageScore = results?.average_score ?? 0;
  const topScore = results?.ranked_candidates?.[0]?.overall_score ?? 0;

  const cards = [
    {
      title: 'Total Resumes',
      value: totalResumes,
      subtitle: `${totalProcessed} screened`,
      icon: Users,
      color: 'text-blue-400',
      bg: 'bg-blue-500/10',
      border: 'border-blue-500/20',
    },
    {
      title: 'Processed & Scored',
      value: totalProcessed,
      subtitle: `${totalResumes - totalProcessed} pending`,
      icon: CheckCircle2,
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/10',
      border: 'border-emerald-500/20',
    },
    {
      title: 'Shortlisted',
      value: totalShortlisted,
      subtitle: totalProcessed > 0 ? `${Math.round((totalShortlisted / totalProcessed) * 100)}% qualification rate` : 'Score ≥ 7.0',
      icon: Star,
      color: 'text-amber-400',
      bg: 'bg-amber-500/10',
      border: 'border-amber-500/20',
    },
    {
      title: 'Average Match Score',
      value: `${averageScore.toFixed(1)} / 10`,
      subtitle: 'Across all applicants',
      icon: TrendingUp,
      color: 'text-indigo-400',
      bg: 'bg-indigo-500/10',
      border: 'border-indigo-500/20',
    },
    {
      title: 'Top Score',
      value: topScore > 0 ? `${topScore.toFixed(1)} / 10` : '—',
      subtitle: results?.ranked_candidates?.[0]?.name ?? 'No rankings yet',
      icon: Award,
      color: 'text-purple-400',
      bg: 'bg-purple-500/10',
      border: 'border-purple-500/20',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
      {cards.map((card, i) => {
        const Icon = card.icon;
        return (
          <div
            key={i}
            className={`p-4 rounded-xl border ${card.border} ${card.bg} backdrop-blur-sm transition-all duration-150 hover:translate-y-[-2px]`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{card.title}</span>
              <Icon className={`w-4 h-4 ${card.color}`} />
            </div>
            <div className="mt-2 text-2xl font-bold text-white tracking-tight">{card.value}</div>
            <div className="mt-1 text-xs text-slate-400 truncate">{card.subtitle}</div>
          </div>
        );
      })}
    </div>
  );
};
