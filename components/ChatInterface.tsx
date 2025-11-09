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
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-10`}>
      <div className={`max-w-3xl w-full ${isUser ? 'bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl px-5 py-4 shadow-sm border border-blue-200' : 'bg-white rounded-xl shadow-sm border border-gray-100'}`}>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className={`flex items-center justify-center w-7 h-7 rounded-full ${isUser ? 'bg-blue-500' : 'bg-gradient-to-br from-blue-600 to-indigo-600'} shadow-sm`}>
              <span className="text-sm">{isUser ? '👤' : '🧬'}</span>
            </div>
            <div>
              <span className={`text-sm font-medium ${isUser ? 'text-blue-900' : 'text-gray-700'}`}>{isUser ? 'You' : 'ToxicoGPT'}</span>
              <span className={`text-xs ${isUser ? 'text-blue-600' : 'text-gray-500'} ml-2`}>{new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
            </div>
          </div>
          {!isUser && (message.consumerSummary || message.content) && (
            <div className="flex items-center gap-1 bg-gray-50 rounded-lg p-0.5 border border-gray-200">
              <button type="button" onClick={() => setViewMode('simple')} className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${viewMode === 'simple' ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-sm' : 'bg-transparent text-gray-600 hover:text-gray-900'}`} aria-pressed={viewMode === 'simple'}>Simple</button>
              <button type="button" onClick={() => setViewMode('technical')} className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${viewMode === 'technical' ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-sm' : 'bg-transparent text-gray-600 hover:text-gray-900'}`} aria-pressed={viewMode === 'technical'}>Technical</button>
            </div>
          )}
        </div>
        <div className={`${isUser ? 'text-gray-800' : 'reader-content'}`}>
          {!isUser ? (
            <div>
              {paragraphs.length > 0 ? (
                <div className="space-y-3">
                  {paragraphs.map((para, idx) => {
                    const { cleanText, citations } = parseCitations(para);
                    // Remove asterisks from display
                    const displayText = cleanText.replace(/\*\*/g, '').replace(/\*/g, '');
                    return (
                      <p key={idx} className="text-[15px] leading-relaxed text-gray-800 font-normal">
                        {displayText}
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
                <p className="text-sm text-gray-500 italic">{viewMode === 'simple' ? 'No simplified summary available. Switch to Technical view for the full response.' : 'No content available.'}</p>
              )}
              {references.length > 0 && (
                <div className="mt-5 pt-5 border-t border-gray-200">
                  <button type="button" onClick={() => setShowReferences(!showReferences)} className="flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors">
                    <span className="text-xs">{showReferences ? '▼' : '►'}</span>
                    <span>Evidence & References ({references.length})</span>
                  </button>
                </div>
              )}
              {showReferences && references.length > 0 && (
                <div className="references-list mt-4">
                  <div className="space-y-2.5">
                    {references.map((ref, idx) => (
                      <div key={idx} id={`ref-${ref.number}`} className="reference-item">
                        <div className="flex items-start gap-2.5">
                          <span className="reference-number">{ref.number}</span>
                          <div className="flex-1">
                            <div>
                              {ref.url !== '#' ? (
                                <a href={ref.url} target="_blank" rel="noopener noreferrer" className="reference-title">{ref.title}</a>
                              ) : (
                                <span className="text-gray-800 font-medium text-sm">{ref.title}</span>
                              )}
                            </div>
                            {ref.excerpt && (<p className="text-[13px] text-gray-600 mt-1.5 leading-relaxed">{ref.excerpt}</p>)}
                            {ref.url !== '#' && (<div className="text-xs text-gray-400 mt-1.5 break-all">{ref.url}</div>)}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-[15px] leading-relaxed">{message.content}</div>
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
    <form onSubmit={handleSubmit} className="p-5 bg-white border-t border-gray-200">
      <div className="max-w-3xl mx-auto flex gap-2">
        <input type="text" value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask about drug interactions, toxicity, or chemical safety..." disabled={disabled} className="flex-1 px-4 py-3 border border-gray-300 bg-white text-gray-800 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 placeholder-gray-400 transition-all text-[15px]" />
        <button type="submit" disabled={disabled || !input.trim()} className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-all shadow-sm hover:shadow disabled:hover:shadow-sm">
          <span className="text-lg">→</span>
        </button>
      </div>
    </form>
  );
};
