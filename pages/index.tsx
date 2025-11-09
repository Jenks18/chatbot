import React, { useState, useEffect, useRef } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { v4 as uuidv4 } from 'uuid';
import { apiService } from '../services/api';
import { ChatMessage, ChatInput } from '../components/ChatInterface';
import { LoadingSpinner, ErrorMessage, WelcomeMessage } from '../components/UIComponents';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  evidence?: Array<any>;
  consumerSummary?: string;
  provenance?: { source: string; evidence_ids?: number[] };
}

export default function Home() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string>('');
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [userMode, setUserMode] = useState<'patient' | 'doctor' | 'researcher'>('patient');
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Check if there's a session ID in the URL
    const urlSessionId = router.query.session as string;
    
    if (urlSessionId) {
      // Load existing session from URL
      setSessionId(urlSessionId);
      localStorage.setItem('toxicogpt_session', urlSessionId);
      loadChatHistory(urlSessionId);
    } else {
      // Check localStorage for existing session
      const storedSessionId = localStorage.getItem('toxicogpt_session');
      if (storedSessionId) {
        // Restore existing session
        setSessionId(storedSessionId);
        router.replace(`/?session=${storedSessionId}`, undefined, { shallow: true });
        loadChatHistory(storedSessionId);
      } else {
        // Create new session and update URL
        const newSessionId = uuidv4();
        setSessionId(newSessionId);
        localStorage.setItem('toxicogpt_session', newSessionId);
        router.replace(`/?session=${newSessionId}`, undefined, { shallow: true });
      }
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
  }, [router.query.session]);

  // Load chat history from backend
  const loadChatHistory = async (sid: string) => {
    if (!sid) return;
    setIsLoadingHistory(true);
    try {
      // Call the admin API to get session history
      const response = await apiService.getSessionHistory(sid);
      if (response && response.messages && response.messages.length > 0) {
        const loadedMessages: Message[] = response.messages.map((msg: any) => ({
          role: msg.role,
          content: msg.content,
          timestamp: new Date(msg.timestamp),
          consumerSummary: msg.consumer_summary || msg.consumerSummary,
          evidence: msg.evidence || [],
          provenance: msg.provenance,
        }));
        setMessages(loadedMessages);
      }
    } catch (err: any) {
      console.error('Failed to load chat history:', err);
      // Don't show error to user, just start fresh
    } finally {
      setIsLoadingHistory(false);
    }
  };

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

  const handleSend = async (message: string) => {
    setError(null);
    
    // Add user message
    const userMessage: Message = {
      role: 'user',
      content: message,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

      try {
      const response = await apiService.sendMessage(message, sessionId, userMode);

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
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get response. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = () => {
    if (confirm('Are you sure you want to start a new chat? This will create a new conversation.')) {
      setMessages([]);
      const newSessionId = uuidv4();
      setSessionId(newSessionId);
      localStorage.setItem('toxicogpt_session', newSessionId);
      // Update URL with new session ID
      router.push(`/?session=${newSessionId}`, undefined, { shallow: true });
    }
  };

  return (
    <>
      <Head>
        <title>DrugInteract AI - Drug Interaction Analysis</title>
        <meta name="description" content="AI-powered drug-drug interaction analysis and polypharmacy risk assessment" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
      </Head>

      <div className="flex flex-col h-screen bg-gradient-to-b from-gray-50 via-white to-gray-50">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
          <div className="max-w-6xl mx-auto flex justify-between items-center">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-9 h-9 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg">
                <span className="text-xl">🧬</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">ToxicoGPT</h1>
                <p className="text-xs text-gray-600 font-medium">Evidence-Based Toxicology AI</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              {isHealthy !== null && (
                <div className="flex items-center gap-2 px-2.5 py-1.5 bg-gray-50 rounded-md border border-gray-200">
                  <div className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-emerald-500' : 'bg-red-500'}`}></div>
                  <span className="text-xs font-medium text-gray-700">
                    {isHealthy ? 'Online' : 'Offline'}
                  </span>
                </div>
              )}
              {healthError && (
                <div className="text-xs text-red-600 max-w-xs truncate">
                  {healthError}
                </div>
              )}
              {messages.length > 0 && (
                <button
                  onClick={handleClearChat}
                  className="px-3 py-1.5 bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 rounded-md text-sm font-medium transition-all flex items-center gap-1.5"
                >
                  <span className="text-base">+</span>
                  New Chat
                </button>
              )}

              {messages.length > 0 && sessionId && (
                <button
                  onClick={() => {
                    const url = `${window.location.origin}/?session=${sessionId}`;
                    navigator.clipboard.writeText(url);
                    alert('Chat link copied to clipboard! Share this link to continue this conversation on any device.');
                  }}
                  className="px-3 py-1.5 bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 rounded-md text-sm font-medium transition-all flex items-center gap-1.5"
                  title="Copy shareable link"
                >
                  <span className="text-base">🔗</span>
                  Share
                </button>
              )}
              
              <a
                href="/admin"
                className="px-3 py-1.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-md hover:from-blue-700 hover:to-indigo-700 text-sm font-medium transition-all shadow-sm"
              >
                Admin
              </a>
            </div>
          </div>
        </header>

        {/* Chat Area */}
        <main className="flex-1 overflow-y-auto bg-white">
            <div className="max-w-3xl mx-auto px-6 py-8">
              {isLoadingHistory ? (
                <div className="flex items-center justify-center py-16">
                  <div className="flex flex-col items-center gap-3">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                    <span className="text-sm text-gray-600 font-medium">Loading conversation...</span>
                  </div>
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
        <div className="bg-white border-t border-gray-200 shadow-sm">
          <div className="max-w-3xl mx-auto">
            <ChatInput onSend={handleSend} disabled={loading || !isHealthy} />
          </div>
        </div>

        {/* Footer */}
        <footer className="bg-gray-50 border-t border-gray-200 px-6 py-3">
          <div className="max-w-6xl mx-auto">
            <p className="text-xs text-center text-gray-600">
              ⚠️ For educational and research purposes only. Not a substitute for professional medical advice. Always consult healthcare professionals for medical decisions.
            </p>
          </div>
        </footer>
      </div>
    </>
  );
}
