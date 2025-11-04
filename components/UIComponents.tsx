import React from 'react';

export const LoadingSpinner: React.FC = () => {
  return (
    <div className="flex justify-start mb-4">
      <div className="bg-slate-800 rounded-lg px-4 py-3">
        <div className="flex items-center gap-2">
          <div className="flex gap-1">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
          </div>
          <span className="text-sm text-slate-400">ToxicoGPT is thinking...</span>
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
    <div className="bg-red-900/20 border border-red-800 rounded-lg p-4 mb-4">
      <div className="flex items-start gap-3">
        <span className="text-red-400 text-xl">⚠️</span>
        <div className="flex-1">
          <p className="text-sm text-red-300">{message}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-2 text-sm text-red-400 hover:text-red-300 transition"
            >
              Try again
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
      className={`bg-slate-800 border border-slate-700 rounded-lg p-5 shadow-sm transition ${onSelectCategory ? 'cursor-pointer hover:bg-slate-700 hover:border-emerald-500/50' : ''}`}
    >
      <div className="text-2xl mb-2">{emoji}</div>
      <h3 className="font-semibold mb-1 text-slate-100">{title}</h3>
      <p className="text-sm text-slate-400">{desc}</p>
    </div>
  );

  return (
    <div className="text-center py-12 px-4">
      <div className="text-6xl mb-4">🧬</div>
      <h2 className="text-3xl font-bold text-slate-100 mb-2">
        Welcome to ToxicoGPT
      </h2>
      <p className="text-slate-400 mb-8 max-w-2xl mx-auto">
        Your AI-powered toxicology assistant. Ask questions about drug toxicity, chemical safety,
        dose-response relationships, and more.
      </p>
      <div className="grid md:grid-cols-3 gap-4 max-w-4xl mx-auto text-left">
        <Card
          emoji="💊"
          title="Drug Toxicity"
          desc="Learn about adverse effects, overdose symptoms, and safety profiles"
          prompt={'Drug Toxicity: Learn about adverse effects, overdose symptoms, and safety profiles'}
        />
        <Card
          emoji="⚗️"
          title="Chemical Safety"
          desc="Understand hazards, exposure limits, and handling procedures"
          prompt={'Chemical Safety: Understand hazards, exposure limits, and handling procedures'}
        />
        <Card
          emoji="📊"
          title="Risk Assessment"
          desc="Explore dose-response data and toxicological pathways"
          prompt={'Risk Assessment: Explore dose-response data and toxicological pathways'}
        />
      </div>
    </div>
  );
};
