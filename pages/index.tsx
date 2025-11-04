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
  consumerSummary?: string;
  provenance?: { source: string; evidence_ids?: number[] };
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string>('');
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [userMode, setUserMode] = useState<'patient' | 'doctor' | 'researcher'>('patient');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Generate session ID
    const newSessionId = uuidv4();
    setSessionId(newSessionId);
    localStorage.setItem('toxicogpt_session', newSessionId);

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
    if (confirm('Are you sure you want to clear the chat history?')) {
      setMessages([]);
      const newSessionId = uuidv4();
      setSessionId(newSessionId);
      localStorage.setItem('toxicogpt_session', newSessionId);
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

      <div className="flex flex-col h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
        {/* Header */}
        <header className="bg-gradient-to-r from-slate-900 to-slate-800 border-b-2 border-slate-700/50 px-6 py-5 shadow-2xl backdrop-blur-sm">
          <div className="max-w-7xl mx-auto flex justify-between items-center">
            <div className="flex items-center gap-4">
              <div className="flex items-center justify-center w-12 h-12 bg-gradient-to-br from-emerald-600 to-emerald-700 rounded-xl shadow-lg">
                <span className="text-3xl">🧬</span>
              </div>
              <div>
                <h1 className="text-2xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-emerald-600">ToxicoGPT</h1>
                <p className="text-sm text-slate-400 font-medium">Evidence-Based Toxicology AI</p>
              </div>
            </div>
            <div className="flex items-center gap-5">
              {isHealthy !== null && (
                <div className="flex items-center gap-2 px-3 py-2 bg-slate-800/50 rounded-lg border border-slate-700">
                  <div className={`w-2.5 h-2.5 rounded-full ${isHealthy ? 'bg-emerald-500 shadow-lg shadow-emerald-500/50 animate-pulse' : 'bg-red-500 shadow-lg shadow-red-500/50'}`}></div>
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
                className="text-sm text-slate-400 hover:text-emerald-400 transition-colors font-medium"
              >
                Clear Chat
              </button>
              
              <a
                href="/admin"
                className="px-4 py-2 bg-gradient-to-r from-slate-700 to-slate-800 text-slate-300 hover:text-white rounded-lg hover:from-slate-600 hover:to-slate-700 text-sm font-semibold transition-all shadow-md hover:shadow-lg border border-slate-600"
              >
                Admin
              </a>
            </div>
          </div>
        </header>

        {/* Chat Area */}
        <main className="flex-1 overflow-y-auto bg-gradient-to-b from-transparent to-slate-950/50">
            <div className="max-w-5xl mx-auto px-6 py-8">
              {messages.length === 0 ? (
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
        <div className="bg-gradient-to-r from-slate-900 to-slate-800 border-t-2 border-slate-700/50 shadow-2xl backdrop-blur-sm">
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
