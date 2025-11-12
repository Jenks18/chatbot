import React from 'react';

export const LoadingSpinner: React.FC = () => {
  return (
    <div className="flex justify-start mb-6">
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl px-6 py-5 border border-slate-700">
        <div className="flex items-center gap-3">
          <div className="flex gap-1.5">
            <div className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce shadow-lg shadow-blue-500/50" style={{ animationDelay: '0ms' }}></div>
            <div className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce shadow-lg shadow-blue-500/50" style={{ animationDelay: '150ms' }}></div>
            <div className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce shadow-lg shadow-blue-500/50" style={{ animationDelay: '300ms' }}></div>
          </div>
          <span className="text-sm text-slate-300 font-medium">Kandih ToxWiki is analyzing...</span>
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
  userMode?: 'patient' | 'doctor' | 'researcher';
  onModeChange?: (mode: 'patient' | 'doctor' | 'researcher') => void;
}

export const WelcomeMessage: React.FC<WelcomeProps> = ({ onSelectCategory, userMode = 'patient', onModeChange }) => {
  const send = (p: string) => {
    if (onSelectCategory) onSelectCategory(p);
  };

  const ModePill: React.FC<{ mode: 'patient' | 'doctor' | 'researcher'; label: string; emoji: string }> = ({ mode, label, emoji }) => (
    <button
      onClick={() => onModeChange && onModeChange(mode)}
      className={`px-4 sm:px-6 py-2 sm:py-3 rounded-full font-semibold text-xs sm:text-sm transition-all duration-300 flex items-center gap-1.5 sm:gap-2 ${
        userMode === mode
          ? 'bg-gradient-to-r from-blue-600 to-indigo-700 text-white shadow-lg shadow-blue-500/30 scale-105'
          : 'bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-slate-300 border-2 border-slate-700'
      }`}
    >
      <span className="text-base sm:text-lg">{emoji}</span>
      <span className="hidden sm:inline">{label}</span>
      <span className="sm:hidden">{label.slice(0, 3)}</span>
    </button>
  );

  // Mode-specific welcome text
  const getModeDescription = () => {
    switch(userMode) {
      case 'patient':
        return 'I\'ll explain everything in simple, easy-to-understand language and ask questions to better understand your needs.';
      case 'doctor':
        return 'I\'ll provide clinical guidance with appropriate medical terminology and evidence-based recommendations.';
      case 'researcher':
        return 'I\'ll deliver comprehensive technical analysis with detailed mechanisms and extensive scientific literature citations.';
      default:
        return 'Your AI-powered toxicology assistant.';
    }
  };

  return (
    <div className="text-center py-8 sm:py-16 px-4 sm:px-6">
      <div className="mb-4 sm:mb-6 inline-flex items-center justify-center w-16 h-16 sm:w-24 sm:h-24 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl sm:rounded-3xl shadow-2xl shadow-blue-500/30">
        <span className="text-4xl sm:text-6xl">🧬</span>
      </div>
      <h2 className="text-2xl sm:text-4xl font-extrabold text-slate-100 mb-2 sm:mb-3 bg-gradient-to-r from-slate-100 to-slate-300 bg-clip-text text-transparent px-4">
        Welcome to Kandih ToxWiki
      </h2>
      
      {/* Mode Selector Pills */}
      <div className="flex justify-center gap-2 sm:gap-4 mb-6 sm:mb-8 flex-wrap px-2">
        <ModePill mode="patient" label="Patient" emoji="👤" />
        <ModePill mode="doctor" label="Doctor" emoji="⚕️" />
        <ModePill mode="researcher" label="Researcher" emoji="🔬" />
      </div>
      
      <p className="text-sm sm:text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed px-4">
        {getModeDescription()}
      </p>
    </div>
  );
};
;
