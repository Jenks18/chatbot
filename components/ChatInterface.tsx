import React from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string | Date;
  evidence?: Array<{
    id: number;
    drug_name: string;
    title?: string;
    summary: string;
    evidence_quality?: string;
    references?: Array<{ id: number; title: string; url: string; excerpt?: string; unverified?: boolean }>;
  }>;
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

const parseReferences = (text: string): Array<{ number: number; citation: string }> => {
  const referencesMatch = text.match(/References?:\s*\n([\s\S]+)$/i);
  if (!referencesMatch) return [];
  
  const referencesSection = referencesMatch[1];
  const lines = referencesSection.split('\n');
  const references: Array<{ number: number; citation: string }> = [];
  
  for (const line of lines) {
    const match = line.match(/^\[(\d+)\]\s*(.+)$/);
    if (match) {
      references.push({
        number: parseInt(match[1]),
        citation: match[2].trim()
      });
    }
  }
  
  return references;
};

const removeReferencesSection = (text: string): string => {
  return text.replace(/\n*References?:\s*\n[\s\S]+$/i, '').trim();
};

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
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

  // Get display content and extract references from AI response
  const displayContent = message.content;
  const contentWithoutRefs = removeReferencesSection(displayContent || '');
  const aiReferences = parseReferences(displayContent || '');
  
  // Combine evidence-based references with AI-generated references
  const evidenceRefs = buildReferences();
  const allReferences = aiReferences.length > 0 
    ? aiReferences.map(ref => ({ 
        number: ref.number, 
        title: ref.citation, 
        url: '#', 
        excerpt: undefined 
      }))
    : evidenceRefs;
  
  const paragraphs = formatContent(contentWithoutRefs);

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 xs:mb-5 sm:mb-6 md:mb-8`}>
      <div className={`max-w-full xs:max-w-[95%] sm:max-w-4xl w-full ${isUser ? 'bg-gradient-to-br from-slate-700 to-slate-800 text-white rounded-xl sm:rounded-2xl px-3 xs:px-4 sm:px-5 md:px-6 py-3 xs:py-4 sm:py-5 shadow-lg border border-slate-600' : 'bg-transparent'}`}>
        <div className="flex items-start justify-between mb-2 xs:mb-3 sm:mb-4 flex-col xs:flex-row gap-2">
          <div className="flex items-center gap-2 xs:gap-2.5 sm:gap-3 min-w-0">
            <div className={`flex items-center justify-center w-6 h-6 xs:w-7 xs:h-7 sm:w-8 sm:h-8 rounded-full flex-shrink-0 ${isUser ? 'bg-slate-600' : 'bg-blue-600 shadow-lg shadow-blue-500/30'}`}>
              <span className="text-sm xs:text-base sm:text-lg">{isUser ? '👤' : '🧬'}</span>
            </div>
            <div className="min-w-0 flex-1">
              <span className="text-[10px] xs:text-xs sm:text-sm font-semibold text-slate-200 block truncate">{isUser ? 'You' : 'Kandih ToxWiki'}</span>
              <span className="text-[9px] xs:text-[10px] sm:text-xs text-slate-400">{new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
            </div>
          </div>
        </div>
        <div className={`${isUser ? 'text-slate-100 text-xs xs:text-sm sm:text-base' : 'reader-content'}`}>
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
                <p className="text-sm text-slate-400 italic">No content available.</p>
              )}
              {allReferences.length > 0 && (
                <div className="mt-6">
                  <button type="button" onClick={() => setShowReferences(!showReferences)} className="flex items-center gap-2 text-sm font-semibold text-blue-400 hover:text-blue-300 transition-colors">
                    <span>{showReferences ? '▼' : '►'}</span>
                    <span>References ({allReferences.length})</span>
                  </button>
                </div>
              )}
              {showReferences && allReferences.length > 0 && (
                <div className="references-list mt-6">
                  <h3 className="text-lg font-bold text-slate-200 mb-4 flex items-center gap-2">
                    <span>📚</span>
                    <span>References</span>
                  </h3>
                  <div className="space-y-4">
                    {allReferences.map((ref, idx) => {
                      // Parse citation to extract title, journal, year, etc.
                      const citation = ref.title || '';
                      
                      // Try to extract structured parts from citation
                      // Format examples:
                      // "Smith et al. Journal Name. 2023;10(2):123-456. PMID: 12345"
                      // "FDA Drug Label - Acetaminophen, Food and Drug Administration, 2024"
                      const parts = citation.split(/[.,;]/);
                      const mainTitle = parts[0]?.trim() || citation;
                      const restOfCitation = parts.slice(1).join(', ').trim();
                      
                      return (
                        <div key={idx} id={`ref-${ref.number}`} className="reference-item">
                          <div className="flex items-start gap-3">
                            <span className="reference-number">{ref.number}</span>
                            <div className="flex-1">
                              <div>
                                {ref.url !== '#' ? (
                                  <a href={ref.url} target="_blank" rel="noopener noreferrer" className="reference-title hover:text-blue-300 transition-colors">
                                    {mainTitle}
                                  </a>
                                ) : (
                                  <div className="text-slate-200 font-semibold text-sm leading-relaxed">
                                    {mainTitle}
                                  </div>
                                )}
                              </div>
                              {restOfCitation && (
                                <p className="text-sm text-slate-400 mt-2 leading-relaxed">
                                  {restOfCitation}
                                </p>
                              )}
                              {ref.excerpt && (
                                <p className="text-sm text-slate-400 mt-2 leading-relaxed italic">
                                  {ref.excerpt}
                                </p>
                              )}
                              {ref.url !== '#' && (
                                <div className="text-xs text-slate-500 mt-2 break-all font-mono">
                                  {ref.url}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })}
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
    <form onSubmit={handleSubmit} className="p-2 xs:p-2.5 sm:p-3 md:p-4">
      <div className="flex gap-1.5 xs:gap-2 sm:gap-3">
        <input 
          type="text" 
          value={input} 
          onChange={(e) => setInput(e.target.value)} 
          placeholder="Ask about medications..." 
          disabled={disabled} 
          className="flex-1 min-w-0 px-2.5 xs:px-3 sm:px-4 md:px-5 py-2 xs:py-2.5 sm:py-3 md:py-3.5 text-xs xs:text-sm sm:text-base border border-slate-600 bg-slate-700 text-slate-100 rounded-lg sm:rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 placeholder-slate-400 placeholder:text-xs placeholder:xs:text-sm transition-all" 
        />
        <button 
          type="submit" 
          disabled={disabled || !input.trim()} 
          className="px-3 xs:px-4 sm:px-6 md:px-8 py-2 xs:py-2.5 sm:py-3 md:py-3.5 bg-gradient-to-r from-blue-600 to-indigo-700 text-white rounded-lg sm:rounded-xl hover:from-blue-700 hover:to-indigo-800 disabled:opacity-50 disabled:cursor-not-allowed font-semibold transition-all shadow-lg flex-shrink-0"
        >
          <span className="text-base xs:text-lg sm:text-xl">→</span>
        </button>
      </div>
    </form>
  );
};
