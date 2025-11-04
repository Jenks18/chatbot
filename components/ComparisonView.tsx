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
    <div className="comparison-view max-w-6xl mx-auto">
      {hasStructuredData && (
        <div className="mb-6 p-5 bg-gradient-to-r from-emerald-900/20 to-blue-900/20 border-2 border-emerald-800/50 rounded-2xl backdrop-blur-sm">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-12 h-12 bg-emerald-600 rounded-xl shadow-lg">
              <span className="text-3xl">💊</span>
            </div>
            <div>
              <p className="font-bold text-lg text-emerald-100">Structured Drug Analysis</p>
              <p className="text-sm text-emerald-300">
                {hasTable ? 'Comparison matrix with detailed interactions' : 'Comprehensive drug profile with citations'}
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="prose prose-lg max-w-none dark:prose-invert markdown-content
                      prose-headings:text-slate-100 
                      prose-h2:text-2xl prose-h2:font-bold prose-h2:mt-8 prose-h2:mb-4 prose-h2:pb-3 prose-h2:border-b-2 prose-h2:border-emerald-600
                      prose-h3:text-xl prose-h3:font-semibold prose-h3:mt-6 prose-h3:mb-3 prose-h3:text-emerald-400
                      prose-p:text-slate-200 prose-p:leading-relaxed prose-p:text-base
                      prose-strong:text-emerald-300 prose-strong:font-semibold
                      prose-ul:my-3 prose-li:my-2 prose-li:text-slate-200
                      prose-table:w-full prose-table:border-collapse prose-table:my-6
                      prose-th:bg-emerald-900/40 prose-th:p-4 prose-th:text-left prose-th:font-bold prose-th:text-emerald-300 prose-th:border-2 prose-th:border-slate-700
                      prose-td:border-2 prose-td:border-slate-700 prose-td:p-4 prose-td:text-slate-200
                      prose-tr:hover:bg-slate-800/50 prose-tr:transition-colors
                      prose-code:text-emerald-400 prose-code:bg-slate-800 prose-code:px-2 prose-code:py-1 prose-code:rounded prose-code:text-sm
                      prose-a:text-emerald-400 prose-a:no-underline prose-a:font-medium hover:prose-a:text-emerald-300 hover:prose-a:underline">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {content}
        </ReactMarkdown>
      </div>

      {/* Enhanced severity indicators legend */}
      {content.toLowerCase().includes('severity') && (
        <div className="mt-8 p-6 bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl border-2 border-slate-700 shadow-xl">
          <h4 className="font-bold text-lg mb-5 text-slate-100 flex items-center gap-2">
            <span className="text-2xl">⚕️</span>
            <span>Interaction Severity Legend</span>
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="info-card bg-red-900/20 border-red-800/50">
              <div className="flex items-center gap-3">
                <div className="w-4 h-4 rounded-full bg-red-500 shadow-lg shadow-red-500/50"></div>
                <div>
                  <div className="font-semibold text-red-300">Major Risk</div>
                  <div className="text-sm text-red-400/80">Avoid combination</div>
                </div>
              </div>
            </div>
            <div className="info-card bg-yellow-900/20 border-yellow-800/50">
              <div className="flex items-center gap-3">
                <div className="w-4 h-4 rounded-full bg-yellow-500 shadow-lg shadow-yellow-500/50"></div>
                <div>
                  <div className="font-semibold text-yellow-300">Moderate Risk</div>
                  <div className="text-sm text-yellow-400/80">Monitor closely</div>
                </div>
              </div>
            </div>
            <div className="info-card bg-green-900/20 border-green-800/50">
              <div className="flex items-center gap-3">
                <div className="w-4 h-4 rounded-full bg-green-500 shadow-lg shadow-green-500/50"></div>
                <div>
                  <div className="font-semibold text-green-300">Minor Risk</div>
                  <div className="text-sm text-green-400/80">Usually safe</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Pharmacology info cards */}
      {(content.includes('## PHARMACOLOGY') || content.includes('Mechanism of Action')) && (
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="info-card">
            <div className="info-card-title">
              <span className="text-2xl">🔬</span>
              <span>Pharmacokinetics</span>
            </div>
            <p className="text-sm text-slate-400">
              Review the absorption, distribution, metabolism, and elimination (ADME) properties in the technical details above.
            </p>
          </div>
          <div className="info-card">
            <div className="info-card-title">
              <span className="text-2xl">⚡</span>
              <span>Mechanism of Action</span>
            </div>
            <p className="text-sm text-slate-400">
              Understand how the drug works at the molecular level and its therapeutic effects.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

