import React from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
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

const parseCitations = (text: string): { cleanText: string; citations: string[] } => {
  const citationPattern = /\[(\d+)\]/g;
  const citations: string[] = [];
  let match;
  while ((match = citationPattern.exec(text)) !== null) {
    if (!citations.includes(match[1])) {
      citations.push(match[1]);
    }
  }
  return { cleanText: text, citations };
};

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const [viewMode, setViewMode] = React.useState<'simple' | 'technical'>('simple');
  const [showReferences, setShowReferences] = React.useState(true); // Changed to true by default

  const formatContent = (s: string) => {
    if (!s) return [];
    const paragraphs = s.split(/\n\n+/).filter(p => p.trim());
    return paragraphs.map(p => p.replace(/\n/g, ' ').trim());
  };

  const buildReferences = (): Array<{ number: number; title: string; url: string; excerpt?: string }> => {
    if (!message.evidence || message.evidence.length === 0) return [];
    const refs: Array<{ number: number; title: string; url: string; excerpt?: string }> = [];
    let refNum = 1;
    message.evidence.forEach((ev) => {
      if (ev.references && ev.references.length > 0) {
        ev.references.forEach((r) => {
          refs.push({
            number: refNum++,
            title: r.title || r.url,
            url: r.url,
            excerpt: r.excerpt,
          });
        });
      } else {
        refs.push({
          number: refNum++,
          title: ev.title || ev.drug_name || 'Evidence',
          url: '#',
          excerpt: ev.summary,
        });
      }
    });
    return refs;
  };

  const references = buildReferences();
  const displayContent = viewMode === 'simple' ? message.consumerSummary : message.content;
  const paragraphs = formatContent(displayContent || '');

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-8`}>
      <div className={`max-w-4xl w-full ${isUser ? 'bg-gradient-to-br from-slate-700 to-slate-800 text-white rounded-2xl px-6 py-5 shadow-lg border border-slate-600' : 'bg-transparent'}`}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className={`flex items-center justify-center w-8 h-8 rounded-full ${isUser ? 'bg-slate-600' : 'bg-emerald-600'}`}>
              <span className="text-lg">{isUser ? '👤' : '🧬'}</span>
            </div>
            <div>
              <span className="text-sm font-semibold text-slate-200">{isUser ? 'You' : 'ToxicoGPT'}</span>
              <span className="text-xs text-slate-400 ml-2">{new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
            </div>
          </div>
          {!isUser && (message.consumerSummary || message.content) && (
            <div className="flex items-center gap-2 bg-slate-800 rounded-lg p-1">
              <button type="button" onClick={() => setViewMode('simple')} className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${viewMode === 'simple' ? 'bg-emerald-600 text-white shadow-md' : 'bg-transparent text-slate-400 hover:text-slate-200'}`} aria-pressed={viewMode === 'simple'}>Simple</button>
              <button type="button" onClick={() => setViewMode('technical')} className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${viewMode === 'technical' ? 'bg-emerald-600 text-white shadow-md' : 'bg-transparent text-slate-400 hover:text-slate-200'}`} aria-pressed={viewMode === 'technical'}>Technical</button>
            </div>
          )}
        </div>
        <div className={`${isUser ? 'text-slate-100' : 'reader-content'}`}>
          {!isUser ? (
            <div>
              {paragraphs.length > 0 ? (
                <div className="space-y-4">
                  {paragraphs.map((para, idx) => {
                    const { cleanText, citations } = parseCitations(para);
                    return (
                      <p key={idx} className="text-[1.0625rem] leading-relaxed text-slate-100 font-normal">
                        {cleanText}
                        {citations.length > 0 && citations.map((citNum) => (
                          <sup key={citNum}>
                            <a href={`#ref-${citNum}`} onClick={(e) => { e.preventDefault(); setShowReferences(true); setTimeout(() => { document.getElementById(`ref-${citNum}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' }); }, 100); }} className="citation-link">{citNum}</a>
                          </sup>
                        ))}
                      </p>
                    );
                  })}
                </div>
              ) : (
                <p className="text-sm text-slate-400 italic">{viewMode === 'simple' ? 'No simplified summary available. Switch to Technical view for the full response.' : 'No content available.'}</p>
              )}
              {references.length > 0 && (
                <div className="mt-6">
                  <button type="button" onClick={() => setShowReferences(!showReferences)} className="flex items-center gap-2 text-sm font-semibold text-emerald-400 hover:text-emerald-300 transition-colors">
                    <span>{showReferences ? '▼' : '►'}</span>
                    <span>References ({references.length})</span>
                  </button>
                </div>
              )}
              {showReferences && references.length > 0 && (
                <div className="references-list mt-6">
                  <h3 className="text-lg font-bold text-slate-200 mb-4 flex items-center gap-2">
                    <span>📚</span>
                    <span>References</span>
                  </h3>
                  <div className="space-y-3">
                    {references.map((ref, idx) => (
                      <div key={idx} id={`ref-${ref.number}`} className="reference-item">
                        <div className="flex items-start gap-3">
                          <span className="reference-number">{ref.number}</span>
                          <div className="flex-1">
                            <div>
                              {ref.url !== '#' ? (
                                <a href={ref.url} target="_blank" rel="noopener noreferrer" className="reference-title">{ref.title}</a>
                              ) : (
                                <span className="text-slate-200 font-semibold">{ref.title}</span>
                              )}
                            </div>
                            {ref.excerpt && (<p className="text-sm text-slate-400 mt-2 leading-relaxed">{ref.excerpt}</p>)}
                            {ref.url !== '#' && (<div className="text-xs text-slate-500 mt-2 break-all">{ref.url}</div>)}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-base leading-relaxed">{message.content}</div>
          )}
        </div>
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
      <div className="flex gap-3">
        <input type="text" value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask about drug interactions, toxicity, or chemical safety..." disabled={disabled} className="flex-1 px-5 py-4 border border-slate-600 bg-slate-700 text-slate-100 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent disabled:opacity-50 placeholder-slate-400 transition-all" />
        <button type="submit" disabled={disabled || !input.trim()} className="px-8 py-4 bg-gradient-to-r from-emerald-600 to-emerald-700 text-white rounded-xl hover:from-emerald-700 hover:to-emerald-800 disabled:opacity-50 disabled:cursor-not-allowed font-semibold transition-all shadow-lg hover:shadow-xl disabled:hover:shadow-lg transform hover:scale-105 disabled:hover:scale-100">
          <span className="text-xl">→</span>
        </button>
      </div>
    </form>
  );
};
