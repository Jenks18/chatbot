import React, { useState, useEffect, useRef } from 'react';
import Head from 'next/head';
import { v4 as uuidv4 } from 'uuid';
import { apiService } from '../services/api';
import { ChatMessage, ChatInput } from '../components/ChatInterface';
import { LoadingSpinner, ErrorMessage, WelcomeMessage } from '../components/UIComponents';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  evidence?: Array<any>;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string>('');
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [userMode, setUserMode] = useState<'patient' | 'doctor' | 'researcher'>('patient');
  const [loadingHistory, setLoadingHistory] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Check if session ID is in URL (for shared links)
    const urlParams = new URLSearchParams(window.location.search);
    const urlSessionId = urlParams.get('session');
    
    if (urlSessionId) {
      // Existing session from URL - load it
      setSessionId(urlSessionId);
      localStorage.setItem('kandih_toxwiki_session', urlSessionId);
      loadChatHistory(urlSessionId);
    } else {
      // Check if there's a session in localStorage with existing chat
      const storedSessionId = localStorage.getItem('kandih_toxwiki_session');
      if (storedSessionId) {
        // Check if this session has messages in database
        loadChatHistory(storedSessionId).then((hasMessages) => {
          if (hasMessages) {
            // Session has history, keep it and update URL
            setSessionId(storedSessionId);
            const newUrl = `${window.location.pathname}?session=${storedSessionId}`;
            window.history.replaceState({}, '', newUrl);
          } else {
            // Empty session, clear it - user will get new session on first message
            localStorage.removeItem('kandih_toxwiki_session');
            setSessionId('');
          }
        });
      }
      // If no session at all, leave empty - will be created on first message
    }

    // Check API health (with retry)
  const checkHealth = async () => {
      try {
        // First try via the frontend API service (axios)
        const res = await apiService.checkHealth();
        if (res?.status === 'healthy') {
          setIsHealthy(true);
          setHealthError(null);
          return;
        }
        // If service returned but not healthy, show message
        setIsHealthy(false);
        setHealthError(`Backend reported status: ${res?.status}`);
      } catch (err: any) {
        console.error('Health check failed (axios):', err?.message || err);
        // Try a fallback fetch directly to the env-specified URL so we can capture CORS/low-level errors
        try {
          const base = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
          const r = await fetch(`${base}/health`, { method: 'GET' });
          if (r.ok) {
            setIsHealthy(true);
            setHealthError(null);
            return;
          } else {
            setIsHealthy(false);
            setHealthError(`Fallback fetch failed: ${r.status} ${r.statusText}`);
          }
        } catch (fe: any) {
          console.error('Health check failed (fetch):', fe?.message || fe);
          setIsHealthy(false);
          setHealthError(fe?.message ? String(fe.message) : 'Unknown network error');
        }
        // Retry after 3 seconds
        setTimeout(checkHealth, 3000);
      }
    };
    checkHealth();
  }, []);

  // Expose manual test function for the UI
  const handleTestHealth = async () => {
    setHealthError(null);
    try {
      const res = await apiService.checkHealth();
      if (res?.status === 'healthy') {
        setIsHealthy(true);
        setHealthError('');
        return;
      }
      setIsHealthy(false);
      setHealthError(`Backend reported status: ${res?.status}`);
    } catch (err: any) {
      try {
        const base = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const r = await fetch(`${base}/health`, { method: 'GET' });
        if (r.ok) {
          setIsHealthy(true);
          setHealthError('');
          return;
        }
        setIsHealthy(false);
        setHealthError(`Fallback fetch failed: ${r.status} ${r.statusText}`);
      } catch (fe: any) {
        setIsHealthy(false);
        setHealthError(fe?.message ? String(fe.message) : 'Unknown network error');
      }
    }
  };

  useEffect(() => {
    // Auto-scroll to bottom
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Listen for postMessage requests from WordPress widget iframe
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      // Security: Only accept messages from your WordPress domain
      // You can add your WordPress domain here for additional security
      // if (event.origin !== 'https://your-wordpress-site.com') return;
      
      if (event.data.type === 'GET_SESSION_ID') {
        // Get current session ID from URL if it exists
        const urlParams = new URLSearchParams(window.location.search);
        const currentSessionId = urlParams.get('session') || sessionId;
        
        // Send session ID back to parent window (WordPress)
        event.source?.postMessage(
          {
            type: 'SESSION_ID_RESPONSE',
            sessionId: currentSessionId
          },
          event.origin as any
        );
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [sessionId]);

  const loadChatHistory = async (sid: string): Promise<boolean> => {
    setLoadingHistory(true);
    try {
      const history = await apiService.getChatHistory(sid, 100);
      if (history && history.history && history.history.length > 0) {
        // Convert chat logs to message format
        const loadedMessages: Message[] = [];
        for (const log of history.history) {
          // Add user message
          loadedMessages.push({
            role: 'user',
            content: log.question,
            timestamp: new Date(log.created_at),
          });
          // Add assistant message
          loadedMessages.push({
            role: 'assistant',
            content: log.answer,
            timestamp: new Date(log.created_at),
            evidence: log.extra_metadata?.evidence || undefined,
          });
        }
        setMessages(loadedMessages);
        return true; // Has messages
      }
      return false; // No messages
    } catch (err) {
      console.error('Failed to load chat history:', err);
      return false;
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleSend = async (message: string) => {
    setError(null);
    
    // Create session on FIRST message if it doesn't exist
    let currentSessionId = sessionId;
    if (!currentSessionId) {
      currentSessionId = uuidv4();
      setSessionId(currentSessionId);
      localStorage.setItem('kandih_toxwiki_session', currentSessionId);
      // Update URL with new session ID
      const newUrl = `${window.location.pathname}?session=${currentSessionId}`;
      window.history.replaceState({}, '', newUrl);
    }
    
    // Add user message
    const userMessage: Message = {
      role: 'user',
      content: message,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

      try {
      const response = await apiService.sendMessage(
        message, 
        currentSessionId, 
        userMode,
        undefined // No user ID without Clerk
      );

      // Add assistant response with evidence
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(),
        evidence: response.evidence,
      };
      setMessages((prev) => [...prev, assistantMessage]);
      
      // Notify parent window (WordPress widget) that session is active
      if (window.parent !== window) {
        try {
          window.parent.postMessage({
            type: 'SESSION_UPDATE',
            sessionId: currentSessionId
          }, '*');
        } catch (e) {
          // Ignore if postMessage fails
        }
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get response. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = () => {
    if (confirm('Are you sure you want to start a new chat?')) {
      setMessages([]);
      setSessionId('');
      localStorage.removeItem('kandih_toxwiki_session');
      // Clear URL parameter
      window.history.pushState({}, '', '/');
    }
  };

  return (
    <>
      <Head>
        <title>Kandih ToxWiki - Drug Interaction Analysis</title>
        <meta name="description" content="AI-powered drug-drug interaction analysis and toxicology information" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
      </Head>

      <div className="flex flex-col h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 overflow-hidden">
        {/* Header - Fully Responsive */}
        <header className="bg-gradient-to-r from-slate-900 to-slate-800 border-b border-blue-700/30 shadow-xl backdrop-blur-sm flex-shrink-0">
          <div className="max-w-7xl mx-auto px-2 xs:px-3 sm:px-4 md:px-6 py-2 xs:py-3 sm:py-4">
            <div className="flex items-center justify-between gap-2">
              {/* Logo and Title - Compact on mobile */}
              <div className="flex items-center gap-2 xs:gap-3 min-w-0 flex-1">
                <div className="flex items-center justify-center w-8 h-8 xs:w-10 xs:h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-lg sm:rounded-xl shadow-lg shadow-blue-500/20 flex-shrink-0">
                  <span className="text-xl xs:text-2xl sm:text-3xl">🧬</span>
                </div>
                <div className="min-w-0 flex-1">
                  <h1 className="text-sm xs:text-base sm:text-xl md:text-2xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-500 truncate">Kandih ToxWiki</h1>
                  <p className="hidden xs:block text-[10px] xs:text-xs sm:text-sm text-slate-400 font-medium truncate">Evidence-Based AI</p>
                </div>
              </div>
              
              {/* Right side controls - Responsive */}
              <div className="flex items-center gap-1.5 xs:gap-2 sm:gap-3 flex-shrink-0">
                {/* Status indicator - Hide on very small screens */}
                {isHealthy !== null && (
                  <div className="hidden md:flex items-center gap-1.5 px-2 py-1 bg-slate-800/50 rounded-md border border-slate-700/50">
                    <div className={`w-1.5 h-1.5 rounded-full ${isHealthy ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
                    <span className="text-[10px] font-medium text-slate-300">{isHealthy ? 'Online' : 'Offline'}</span>
                  </div>
                )}
                
                {/* Clear Chat - Text button on tablet+, icon on mobile */}
                <button
                  onClick={handleClearChat}
                  className="px-2 xs:px-3 py-1.5 text-[10px] xs:text-xs sm:text-sm text-slate-400 hover:text-blue-400 transition-colors font-medium"
                  title="Clear Chat"
                >
                  <span className="hidden xs:inline">Clear</span>
                  <span className="xs:hidden">🗑️</span>
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Chat Area - Fully responsive */}
        <main className="flex-1 overflow-y-auto bg-gradient-to-b from-transparent to-slate-950/50 overscroll-contain">
            <div className="w-full max-w-5xl mx-auto px-2 xs:px-3 sm:px-4 md:px-6 py-3 xs:py-4 sm:py-6 md:py-8">
              {loadingHistory ? (
                <div className="flex flex-col items-center justify-center py-16 xs:py-20 sm:py-24">
                  <div className="animate-spin rounded-full h-8 w-8 xs:h-10 xs:w-10 sm:h-12 sm:w-12 border-b-2 border-blue-500"></div>
                  <p className="mt-3 xs:mt-4 text-xs xs:text-sm sm:text-base text-slate-400">Loading...</p>
                </div>
              ) : messages.length === 0 ? (
                <WelcomeMessage 
                  onSelectCategory={(p) => handleSend(p)} 
                  userMode={userMode}
                  onModeChange={setUserMode}
                />
              ) : (
                <>
                  {messages.map((msg, idx) => (
                    <ChatMessage key={idx} message={msg} />
                  ))}
                  {loading && <LoadingSpinner />}
                  {error && <ErrorMessage message={error} onRetry={() => setError(null)} />}
                  <div ref={messagesEndRef} />
                </>
              )}
            </div>
        </main>

        {/* Input Area - Responsive */}
        <div className="bg-gradient-to-r from-slate-900 to-slate-800 border-t border-blue-700/30 shadow-xl backdrop-blur-sm flex-shrink-0">
          <div className="w-full max-w-5xl mx-auto">
            <ChatInput onSend={handleSend} disabled={loading || !isHealthy} />
          </div>
        </div>

        {/* Footer - Compact */}
        <footer className="bg-slate-900/95 border-t border-slate-800 px-2 xs:px-3 sm:px-4 py-2 xs:py-2.5 sm:py-3 flex-shrink-0">
          <div className="max-w-7xl mx-auto">
            <p className="text-[9px] xs:text-[10px] sm:text-xs text-center text-slate-500 leading-tight xs:leading-relaxed">
              ⚠️ For educational purposes only. Not medical advice. Consult healthcare professionals.
            </p>
          </div>
        </footer>
      </div>
    </>
  );
}
