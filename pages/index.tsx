import React, { useState, useEffect, useRef } from 'react';
import Head from 'next/head';
import { v4 as uuidv4 } from 'uuid';
import { apiService } from '../services/api';
import { ChatMessage, ChatInput } from '../components/ChatInterface';
import { LoadingSpinner, ErrorMessage, WelcomeMessage } from '../components/UIComponents';
import { SignInButton, SignUpButton, UserButton, useUser } from '@clerk/nextjs';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  evidence?: Array<any>;
  consumerSummary?: string;
  provenance?: { source: string; evidence_ids?: number[] };
}

export default function Home() {
  const { isSignedIn, user } = useUser();
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
            consumerSummary: log.extra_metadata?.consumer_summary || undefined,
            provenance: log.extra_metadata?.consumer_summary_provenance || undefined,
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
      const response = await apiService.sendMessage(message, currentSessionId, userMode);

      // Add assistant response (include consumer summary when returned by backend)
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.answer,
        consumerSummary: (response as any).consumer_summary || (response as any).consumerSummary || undefined,
        provenance: (response as any).provenance || undefined,
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

      <div className="flex flex-col h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
        {/* Header */}
        <header className="bg-gradient-to-r from-slate-900 to-slate-800 border-b-2 border-blue-700/30 px-6 py-5 shadow-2xl backdrop-blur-sm">
          <div className="max-w-7xl mx-auto flex justify-between items-center">
            <div className="flex items-center gap-4">
              <div className="flex items-center justify-center w-12 h-12 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl shadow-lg shadow-blue-500/30">
                <span className="text-3xl">🧬</span>
              </div>
              <div>
                <h1 className="text-2xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-500">Kandih ToxWiki</h1>
                <p className="text-sm text-slate-400 font-medium">Evidence-Based Toxicology AI</p>
              </div>
            </div>
            <div className="flex items-center gap-5">
              {isHealthy !== null && (
                <div className="flex items-center gap-2 px-3 py-2 bg-slate-800/50 rounded-lg border border-slate-700">
                  <div className={`w-2.5 h-2.5 rounded-full ${isHealthy ? 'bg-blue-500 shadow-lg shadow-blue-500/50 animate-pulse' : 'bg-red-500 shadow-lg shadow-red-500/50'}`}></div>
                  <span className="text-sm font-semibold text-slate-300">
                    {isHealthy ? 'Online' : 'Offline'}
                  </span>
                </div>
              )}
              {healthError && (
                <div className="text-xs text-red-400 max-w-xs truncate">
                  {healthError}
                </div>
              )}
              <button
                onClick={handleClearChat}
                className="text-sm text-slate-400 hover:text-blue-400 transition-colors font-medium"
              >
                Clear Chat
              </button>
              
              {/* Auth Buttons - OpenEvidence Style */}
              <div className="flex items-center gap-3">
                {!isSignedIn ? (
                  <>
                    <SignInButton mode="modal">
                      <button className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors">
                        Log In
                      </button>
                    </SignInButton>
                    <SignUpButton mode="modal">
                      <button className="px-4 py-2 text-sm font-medium text-white bg-orange-500 rounded-lg hover:bg-orange-600 transition-colors shadow-sm">
                        Sign Up
                      </button>
                    </SignUpButton>
                  </>
                ) : (
                  <>
                    <a
                      href="/admin"
                      className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
                    >
                      Admin
                    </a>
                    <UserButton 
                      afterSignOutUrl="/"
                      appearance={{
                        elements: {
                          avatarBox: "w-9 h-9"
                        }
                      }}
                    />
                  </>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Chat Area */}
        <main className="flex-1 overflow-y-auto bg-gradient-to-b from-transparent to-slate-950/50">
            <div className="max-w-5xl mx-auto px-6 py-8">
              {loadingHistory ? (
                <div className="flex flex-col items-center justify-center py-20">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
                  <p className="mt-4 text-slate-400">Loading conversation history...</p>
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

        {/* Input Area */}
        <div className="bg-gradient-to-r from-slate-900 to-slate-800 border-t-2 border-blue-700/30 shadow-2xl backdrop-blur-sm">
          <div className="max-w-5xl mx-auto">
            <ChatInput onSend={handleSend} disabled={loading || !isHealthy} />
          </div>
        </div>

        {/* Footer */}
        <footer className="bg-slate-900 border-t border-slate-800 px-6 py-4">
          <div className="max-w-7xl mx-auto">
            <p className="text-xs text-center text-slate-500">
              ⚠️ For educational and research purposes only. Not a substitute for professional medical advice. Always consult healthcare professionals for medical decisions.
            </p>
          </div>
        </footer>
      </div>
    </>
  );
}
