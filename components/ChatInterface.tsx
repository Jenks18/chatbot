import React from 'react';
import ReactMarkdown from 'react-markdown';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  // backend may return an ISO string; accept either
  timestamp: string | Date;
  consumerSummary?: string;
  evidence?: Array<{
    id: number;
    drug_name: string;
    title?: string;
    summary: string;
    evidence_quality?: string;
    references?: Array<{ id: number; title: string; url: string; excerpt?: string; unverified?: boolean }>;
  }>;
  provenance?: { source: string; evidence_ids?: number[] };
}

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  
  // Local UI state for assistant message collapsing/expansion and refs
  const [expanded, setExpanded] = React.useState(false);
  const [viewMode, setViewMode] = React.useState<'simple' | 'technical'>('simple');
  const [refsOpen, setRefsOpen] = React.useState(false);
  const refsMap = React.useRef<Record<string, HTMLDivElement | null>>({});

  const scrollToRef = (key: string) => {
    const el = refsMap.current[key];
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  };

  // Produce paragraph-based content preserving paragraph breaks but stripping markdown formatting
  const cleanMarkdown = (s: string) => {
    if (!s) return '';
    // remove markdown headings, bold/italic, codeticks, links
    let out = s.replace(/^#+\s*/gm, '');
    out = out.replace(/\[(.*?)\]\((.*?)\)/g, '$1');
    out = out.replace(/[*_`]/g, '');
    // Preserve paragraph breaks (double newline) but collapse single newlines to spaces
    out = out.replace(/\n{2,}/g, '\n\n'); // normalize multiple breaks to double
    out = out.replace(/([^\n])\n([^\n])/g, '$1 $2'); // single newline becomes space
    // collapse multiple spaces
    out = out.replace(/[ \t]{2,}/g, ' ');
    return out.trim();
  };

  const makeSummary = () => {
    // Server-only: Simple view MUST use only server-provided consumerSummary. Do NOT synthesize on client.
    if (message.consumerSummary && message.consumerSummary.trim()) {
      return cleanMarkdown(message.consumerSummary);
    }
    return '';
  };

  const makeFullContent = () => {
    // Technical view: strip markdown but preserve paragraphs
    if (message.content && message.content.trim()) {
      return cleanMarkdown(message.content);
    }
    return '';
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6`}>
      <div
        className={`max-w-4xl w-full ${
          isUser
            ? 'bg-slate-700 text-white rounded-xl px-5 py-4 shadow-sm'
            : 'text-slate-100'
        }`}
      >
          <div className="flex items-center gap-2 mb-3">
          <span className="text-sm font-medium text-slate-400">
            {isUser ? '👤 You' : '🧬 ToxicoGPT'}
          </span>
          <span className="text-xs text-slate-500">
            {new Date(message.timestamp).toLocaleTimeString()}
          </span>
        </div>
        <div className={`${isUser ? 'text-white' : 'text-slate-100'}`}>
          {/* Assistant message: paragraph-based with inline citations */}
          {!isUser && (
            <div>
              {/* View mode toggle - minimal inline */}
              <div className="mb-4 flex items-center gap-2">
                <span className="text-xs text-slate-400">View:</span>
                <button
                  type="button"
                  onClick={() => setViewMode('simple')}
                  className={`text-xs px-3 py-1.5 rounded-md transition font-medium ${viewMode === 'simple' ? 'bg-emerald-600 text-white shadow-sm' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}`}
                  aria-pressed={viewMode === 'simple'}
                >
                  Simple
                </button>
                <button
                  type="button"
                  onClick={() => setViewMode('technical')}
                  className={`text-xs px-3 py-1.5 rounded-md transition font-medium ${viewMode === 'technical' ? 'bg-emerald-600 text-white shadow-sm' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}`}
                  aria-pressed={viewMode === 'technical'}
                >
                  Technical
                </button>
              </div>

              {/* Paragraph-based content with inline citation numbers */}
              <div className="prose prose-invert max-w-none">
                {viewMode === 'simple' ? (
                  <div>
                    {makeSummary() ? (
                      makeSummary().split('\n\n').map((para, idx) => (
                        <p key={idx} className="mb-4 text-lg leading-relaxed text-slate-100">
                          {para}
                        </p>
                      ))
                    ) : (
                      <p className="text-sm text-slate-400 italic">No short summary available. Switch to Technical to read the full response.</p>
                    )}
                  </div>
                ) : (
                  <div>
                    {makeFullContent() ? (
                      makeFullContent().split('\n\n').map((para, idx) => (
                        <p key={idx} className="mb-4 text-lg leading-relaxed text-slate-100">
                          {para}
                        </p>
                      ))
                    ) : (
                      <p className="text-sm text-slate-400 italic">No content available.</p>
                    )}
                  </div>
                )}

                {/* Inline citation badges (clickable, numbered like [1-2]) */}
                {message.evidence && message.evidence.length > 0 && (
                  <div className="mt-5 flex flex-wrap gap-2 items-center">
                    {message.evidence.map((ev, evIdx) => (
                      <React.Fragment key={ev.id || evIdx}>
                        {ev.references && ev.references.map((r, rIdx) => {
                          const citationNum = evIdx + 1;
                          return (
                            <button
                              key={`cite-${evIdx}-${rIdx}`}
                              type="button"
                              onClick={() => setRefsOpen(true)}
                              className="text-sm bg-slate-700 text-emerald-400 px-2.5 py-1 rounded-md hover:bg-slate-600 transition font-medium border border-slate-600"
                              title={r.title}
                            >
                              [{citationNum}]
                            </button>
                          );
                        })}
                      </React.Fragment>
                    ))}
                  </div>
                )}
              </div>

              {/* Minimal expand/collapse */}
              {!expanded && (
                <div className="mt-4">
                  <button
                    type="button"
                    onClick={() => setExpanded(true)}
                    className="text-sm text-emerald-400 hover:text-emerald-300 transition"
                  >
                    Show references →
                  </button>
                </div>
              )}
            </div>
          )}

          {/* User message: simple display */}
          {isUser && (
            <div className="text-base leading-relaxed">{message.content}</div>
          )}
        </div>

        {/* Expandable references section */}
        {!isUser && expanded && message.evidence && message.evidence.length > 0 && (
          <div className="mt-6 pt-4 border-t border-slate-700">
            <div className="text-sm font-semibold mb-3 text-slate-300">References</div>
            <ol className="list-decimal list-inside space-y-3 text-sm">
              {(() => {
                // flatten all references into a single numbered list
                const flat: Array<{ title: string; url: string; excerpt?: string }> = [];
                message.evidence!.forEach((ev) => {
                  (ev.references || []).forEach((r) => {
                    flat.push({ title: r.title || r.url, url: r.url, excerpt: r.excerpt });
                  });
                });
                if (flat.length === 0) {
                  message.evidence!.forEach((ev) => {
                    flat.push({ title: ev.title || ev.drug_name || 'Evidence', url: '#', excerpt: ev.summary });
                  });
                }
                return flat.map((r, idx) => (
                  <li key={idx} className="text-slate-300">
                    <div>
                      <a href={r.url} target="_blank" rel="noreferrer" className="text-emerald-400 hover:text-emerald-300 transition">
                        {r.title}
                      </a>
                    </div>
                    {r.excerpt && (<div className="text-xs text-slate-400 mt-1">{r.excerpt}</div>)}
                  </li>
                ));
              })()}
            </ol>
          </div>
        )}

        {/* References dialog (modal) */}
        {refsOpen && message.evidence && message.evidence.length > 0 && (
          <div role="dialog" aria-label="References" className="fixed right-6 bottom-6 w-96 max-h-[70vh] overflow-auto bg-slate-800 border border-slate-600 rounded-xl p-5 shadow-2xl z-50">
            <div className="flex justify-between items-center mb-3">
              <div className="font-semibold text-slate-100">References</div>
              <button type="button" onClick={() => setRefsOpen(false)} aria-label="Close references" className="text-sm text-slate-400 hover:text-slate-200 transition">✕</button>
            </div>
            {message.provenance && message.provenance.source && (
              <div className="text-xs text-slate-400 mb-3 pb-3 border-b border-slate-700">
                {`Based on: ${message.provenance.source}${message.provenance.evidence_ids && message.provenance.evidence_ids.length ? ` (sources: ${message.provenance.evidence_ids.join(',')})` : ''}`}
              </div>
            )}
            <div className="space-y-3 text-sm">
              {message.evidence.map((ev, evIdx) => (
                <div key={ev.id || evIdx} className="pb-3 border-b border-slate-700 last:border-0">
                  <div className="font-medium text-slate-100">{ev.title || ev.drug_name}</div>
                  <div className="text-xs text-slate-400 mt-1">{ev.summary}</div>
                  {ev.references && (
                    <ul className="mt-2 space-y-1 text-xs">
                      {ev.references.map((r, rIdx) => (
                        <li key={`ref-${evIdx}-${rIdx}`} className="flex items-start gap-2">
                          <span className="text-emerald-400 font-mono">[{evIdx + 1}]</span>
                          <a href={r.url} target="_blank" rel="noreferrer" className="text-emerald-400 hover:text-emerald-300 transition flex-1" onClick={() => setRefsOpen(false)}>{r.title}</a>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSend, disabled }) => {
  const [input, setInput] = React.useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-4">
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a follow-up question..."
          disabled={disabled}
          className="flex-1 px-4 py-3 border border-slate-600 bg-slate-800 text-slate-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent disabled:opacity-50 placeholder-slate-500"
        />
        <button
          type="submit"
          disabled={disabled || !input.trim()}
          className="px-6 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold transition-colors shadow-sm"
        >
          ↑
        </button>
      </div>
    </form>
  );
};
