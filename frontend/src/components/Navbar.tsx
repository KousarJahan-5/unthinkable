import React from 'react';
import { Sparkles, Bot, PlayCircle, RefreshCw } from 'lucide-react';
import type { HealthStatus } from '../types';

interface NavbarProps {
  health: HealthStatus | null;
  onSeedDemo: () => void;
  isSeeding: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ health, onSeedDemo, isSeeding }) => {
  return (
    <header className="sticky top-0 z-40 bg-slate-900/80 backdrop-blur-md border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg text-white tracking-tight">Smart Resume Screener</span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
                AI Powered
              </span>
            </div>
            <p className="text-xs text-slate-400">Semantic Matching • Explainable 1-10 Scoring • Recruiter Intelligence</p>
          </div>
        </div>

        {/* Right Actions & Health Status */}
        <div className="flex items-center gap-4">
          {/* LLM Status Indicator */}
          {health && (
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs">
              <Bot className="w-3.5 h-3.5 text-blue-400" />
              <span className="text-slate-300 font-medium">
                {health.llm_configured ? health.llm_model : 'Semantic Engine'}
              </span>
              <span
                className={`w-2 h-2 rounded-full ${
                  health.status === 'healthy' ? 'bg-emerald-400' : 'bg-amber-400'
                }`}
                title={health.evaluation_mode}
              />
            </div>
          )}

          {/* 1-Click Demo CTA */}
          <button
            onClick={onSeedDemo}
            disabled={isSeeding}
            className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 rounded-lg shadow-md shadow-blue-600/25 transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSeeding ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Loading Demo...</span>
              </>
            ) : (
              <>
                <PlayCircle className="w-4 h-4" />
                <span>1-Click Demo</span>
              </>
            )}
          </button>
        </div>
      </div>
    </header>
  );
};
