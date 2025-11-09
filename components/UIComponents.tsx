import React from 'react';

export const LoadingSpinner: React.FC = () => {
  return (
    <div className="flex justify-start mb-6">
      <div className="bg-white rounded-xl px-5 py-4 border border-gray-200 shadow-sm">
        <div className="flex items-center gap-2.5">
          <div className="flex gap-1">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
          </div>
          <span className="text-sm text-gray-700 font-medium">ToxicoGPT is analyzing...</span>
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
    <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6">
      <div className="flex items-start gap-3">
        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-red-100">
          <span className="text-red-600 text-lg">⚠️</span>
        </div>
        <div className="flex-1">
          <h4 className="text-sm font-semibold text-red-900 mb-1">Error</h4>
          <p className="text-sm text-red-700 leading-relaxed">{message}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-2.5 px-3 py-1.5 text-sm font-medium text-red-700 hover:text-red-800 bg-red-100 hover:bg-red-200 rounded-md transition-all"
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
      className={`px-5 py-2.5 rounded-lg font-medium text-sm transition-all flex items-center gap-2 ${
        userMode === mode
          ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-sm'
          : 'bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-300'
      }`}
    >
      <span className="text-base">{emoji}</span>
      {label}
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
    <div className="text-center py-16 px-6">
      <div className="mb-6 inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl shadow-md">
        <span className="text-5xl">🧬</span>
      </div>
      <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600 mb-3">
        Welcome to ToxicoGPT
      </h2>
      
      {/* Mode Selector Pills */}
      <div className="flex justify-center gap-3 mb-6">
        <ModePill mode="patient" label="Patient" emoji="👤" />
        <ModePill mode="doctor" label="Doctor" emoji="⚕️" />
        <ModePill mode="researcher" label="Researcher" emoji="🔬" />
      </div>
      
      <p className="text-base text-gray-600 max-w-2xl mx-auto leading-relaxed">
        {getModeDescription()}
      </p>
    </div>
  );
};
