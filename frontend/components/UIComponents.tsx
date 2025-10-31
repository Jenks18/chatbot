import React from 'react';

export const LoadingSpinner: React.FC = () => {
  return (
    <div className="flex justify-start mb-4">
      <div className="bg-gray-100 dark:bg-gray-800 rounded-lg px-4 py-3">
        <div className="flex items-center gap-2">
          <div className="flex gap-1">
            <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
            <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
            <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
          </div>
          <span className="text-sm text-gray-600 dark:text-gray-400">ToxicoGPT is thinking...</span>
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
    <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-4">
      <div className="flex items-start gap-3">
        <span className="text-red-600 dark:text-red-400 text-xl">⚠️</span>
        <div className="flex-1">
          <p className="text-sm text-red-800 dark:text-red-300">{message}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-2 text-sm text-red-600 dark:text-red-400 hover:underline"
            >
              Try again
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export const WelcomeMessage: React.FC = () => {
  return (
    <div className="text-center py-12 px-4">
      <div className="text-6xl mb-4">🧬</div>
      <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
        Welcome to ToxicoGPT
      </h2>
      <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-2xl mx-auto">
        Your AI-powered toxicology assistant. Ask questions about drug toxicity, chemical safety,
        dose-response relationships, and more.
      </p>
      <div className="grid md:grid-cols-3 gap-4 max-w-4xl mx-auto text-left">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
          <div className="text-2xl mb-2">💊</div>
          <h3 className="font-semibold mb-1 text-gray-900 dark:text-white">Drug Toxicity</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Learn about adverse effects, overdose symptoms, and safety profiles
          </p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
          <div className="text-2xl mb-2">⚗️</div>
          <h3 className="font-semibold mb-1 text-gray-900 dark:text-white">Chemical Safety</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Understand hazards, exposure limits, and handling procedures
          </p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
          <div className="text-2xl mb-2">📊</div>
          <h3 className="font-semibold mb-1 text-gray-900 dark:text-white">Risk Assessment</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Explore dose-response data and toxicological pathways
          </p>
        </div>
      </div>
    </div>
  );
};
