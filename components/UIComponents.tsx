import React from 'react';

export const LoadingSpinner: React.FC = () => {
  return (
    <div className="flex justify-start mb-6">
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl px-6 py-5 border border-slate-700">
        <div className="flex items-center gap-3">
          <div className="flex gap-1.5">
            <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full animate-bounce shadow-lg shadow-emerald-500/50" style={{ animationDelay: '0ms' }}></div>
            <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full animate-bounce shadow-lg shadow-emerald-500/50" style={{ animationDelay: '150ms' }}></div>
            <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full animate-bounce shadow-lg shadow-emerald-500/50" style={{ animationDelay: '300ms' }}></div>
          </div>
          <span className="text-sm text-slate-300 font-medium">ToxicoGPT is analyzing...</span>
        </div>
      </div>
    </div>
  );
};

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({ message, onRetry }) => {
  return (
    <div className="bg-red-900/20 border-2 border-red-800/50 rounded-2xl p-5 mb-6 backdrop-blur-sm">
      <div className="flex items-start gap-4">
        <div className="flex items-center justify-center w-10 h-10 rounded-full bg-red-900/40">
          <span className="text-red-400 text-xl">⚠️</span>
        </div>
        <div className="flex-1">
          <h4 className="text-sm font-semibold text-red-300 mb-1">Error</h4>
          <p className="text-sm text-red-200/90 leading-relaxed">{message}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-3 px-4 py-2 text-sm font-semibold text-red-400 hover:text-red-300 bg-red-900/20 hover:bg-red-900/30 rounded-lg transition-all"
            >
              Try again →
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

interface WelcomeProps {
  onSelectCategory?: (prompt: string) => void;
}

export const WelcomeMessage: React.FC<WelcomeProps> = ({ onSelectCategory }) => {
  const send = (p: string) => {
    if (onSelectCategory) onSelectCategory(p);
  };

  const Card: React.FC<{ emoji: string; title: string; desc: string; prompt: string }> = ({ emoji, title, desc, prompt }) => (
    <div
      role={onSelectCategory ? 'button' : undefined}
      tabIndex={onSelectCategory ? 0 : -1}
      onClick={() => send(prompt)}
      onKeyDown={(e) => { if (onSelectCategory && (e.key === 'Enter' || e.key === ' ')) send(prompt); }}
      className={`group bg-gradient-to-br from-slate-800 to-slate-900 border-2 border-slate-700 rounded-2xl p-6 shadow-lg transition-all duration-300 ${onSelectCategory ? 'cursor-pointer hover:border-emerald-500/70 hover:shadow-2xl hover:shadow-emerald-500/10 hover:scale-105' : ''}`}
    >
      <div className="text-4xl mb-4 transition-transform duration-300 group-hover:scale-110">{emoji}</div>
      <h3 className="font-bold text-lg mb-2 text-slate-100 group-hover:text-emerald-400 transition-colors">{title}</h3>
      <p className="text-sm text-slate-400 leading-relaxed group-hover:text-slate-300 transition-colors">{desc}</p>
    </div>
  );

  return (
    <div className="text-center py-16 px-6">
      <div className="mb-6 inline-flex items-center justify-center w-24 h-24 bg-gradient-to-br from-emerald-600 to-emerald-700 rounded-3xl shadow-2xl shadow-emerald-500/20">
        <span className="text-6xl">🧬</span>
      </div>
      <h2 className="text-4xl font-extrabold text-slate-100 mb-3 bg-gradient-to-r from-slate-100 to-slate-300 bg-clip-text text-transparent">
        Welcome to ToxicoGPT
      </h2>
      <p className="text-lg text-slate-400 mb-12 max-w-2xl mx-auto leading-relaxed">
        Your AI-powered toxicology assistant. Get evidence-based answers about drug interactions,
        chemical safety, toxicity profiles, and more.
      </p>
      <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
        <Card
          emoji="💊"
          title="Drug Interactions"
          desc="Analyze drug-drug interactions, polypharmacy risks, and safety profiles with evidence-based citations"
          prompt="Tell me about common drug interactions with acetaminophen"
        />
        <Card
          emoji="⚗️"
          title="Chemical Safety"
          desc="Understand hazards, exposure limits, handling procedures, and toxicity mechanisms"
          prompt="What are the safety considerations for handling lead compounds?"
        />
        <Card
          emoji="📊"
          title="Toxicity Analysis"
          desc="Explore dose-response relationships, toxicological pathways, and adverse effects"
          prompt="Explain the dose-response relationship and toxicity of acetaminophen"
        />
      </div>
    </div>
  );
};
;
