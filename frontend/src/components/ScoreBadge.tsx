import React from 'react';

interface ScoreBadgeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export const ScoreBadge: React.FC<ScoreBadgeProps> = ({ score, size = 'md', showLabel = false }) => {
  // Determine color scheme based on score
  let bgClass = 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
  let dotClass = 'bg-emerald-400';
  let label = 'Strong Match';

  if (score < 4.5) {
    bgClass = 'bg-rose-500/15 text-rose-400 border-rose-500/30';
    dotClass = 'bg-rose-400';
    label = 'Weak Match';
  } else if (score < 6.5) {
    bgClass = 'bg-amber-500/15 text-amber-400 border-amber-500/30';
    dotClass = 'bg-amber-400';
    label = 'Partial Match';
  } else if (score < 8.0) {
    bgClass = 'bg-blue-500/15 text-blue-400 border-blue-500/30';
    dotClass = 'bg-blue-400';
    label = 'Match';
  }

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 font-medium',
    md: 'text-sm px-2.5 py-1 font-semibold',
    lg: 'text-2xl px-4 py-2 font-bold',
  };

  return (
    <div className="inline-flex items-center gap-1.5">
      <span
        className={`inline-flex items-center gap-1.5 rounded-lg border ${bgClass} ${sizeClasses[size]}`}
      >
        <span className={`w-2 h-2 rounded-full ${dotClass} animate-pulse`} />
        {score.toFixed(1)} <span className="opacity-60 text-xs">/ 10</span>
      </span>
      {showLabel && (
        <span className="text-xs font-medium text-slate-400">
          ({label})
        </span>
      )}
    </div>
  );
};
