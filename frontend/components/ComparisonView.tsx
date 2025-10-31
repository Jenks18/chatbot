import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ComparisonViewProps {
  content: string;
}

export default function ComparisonView({ content }: ComparisonViewProps) {
  // Check if content contains comparison matrix or structured drug data
  const hasTable = content.includes('|') && content.includes('---');
  const hasStructuredData = content.includes('## IDENTIFICATION') || content.includes('## COMPARISON MATRIX');

  return (
    <div className="comparison-view">
      {hasStructuredData && (
        <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <div className="flex items-center gap-2">
            <span className="text-2xl">💊</span>
            <div>
              <p className="font-semibold text-blue-900 dark:text-blue-100">Structured Drug Analysis</p>
              <p className="text-sm text-blue-700 dark:text-blue-300">
                {hasTable ? 'Comparison matrix detected' : 'Detailed drug profile'}
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="prose prose-sm max-w-none dark:prose-invert
                      prose-headings:text-primary-900 dark:prose-headings:text-primary-100
                      prose-h2:text-lg prose-h2:font-bold prose-h2:mt-6 prose-h2:mb-3 prose-h2:pb-2 prose-h2:border-b-2 prose-h2:border-primary-200
                      prose-h3:text-base prose-h3:font-semibold prose-h3:mt-4 prose-h3:mb-2
                      prose-p:text-gray-700 dark:prose-p:text-gray-300
                      prose-strong:text-gray-900 dark:prose-strong:text-gray-100
                      prose-ul:my-2 prose-li:my-1
                      prose-table:w-full prose-table:border-collapse
                      prose-th:bg-primary-100 dark:prose-th:bg-primary-900 prose-th:p-3 prose-th:text-left prose-th:font-semibold
                      prose-td:border prose-td:border-gray-300 dark:prose-td:border-gray-600 prose-td:p-3
                      prose-tr:hover:bg-gray-50 dark:prose-tr:hover:bg-gray-800">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {content}
        </ReactMarkdown>
      </div>

      {/* Severity indicators legend */}
      {content.toLowerCase().includes('severity') && (
        <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <h4 className="font-semibold text-sm mb-3 text-gray-900 dark:text-gray-100">Interaction Severity Legend:</h4>
          <div className="grid grid-cols-3 gap-3 text-sm">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-red-500"></span>
              <span className="text-gray-700 dark:text-gray-300">Major - Avoid combination</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-yellow-500"></span>
              <span className="text-gray-700 dark:text-gray-300">Moderate - Monitor closely</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-green-500"></span>
              <span className="text-gray-700 dark:text-gray-300">Minor - Usually safe</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
