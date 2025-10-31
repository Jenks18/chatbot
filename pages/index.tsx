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
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string>('');
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Generate session ID
    const newSessionId = uuidv4();
    setSessionId(newSessionId);
    localStorage.setItem('toxicogpt_session', newSessionId);

    // Check API health (with retry)
    const checkHealth = async () => {
      try {
        await apiService.checkHealth();
        setIsHealthy(true);
      } catch (error) {
        console.error('Health check failed:', error);
        setIsHealthy(false);
        // Retry after 3 seconds
        setTimeout(checkHealth, 3000);
      }
    };
    checkHealth();
  }, []);

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
      const response = await apiService.sendMessage(message, sessionId);
      
      // Add assistant response
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(),
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

      <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-900">
        {/* Header */}
        <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
          <div className="max-w-7xl mx-auto flex justify-between items-center">
            <div className="flex items-center gap-3">
              <span className="text-3xl">🧬</span>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">ToxicoGPT</h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">Toxicology AI Assistant</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              {isHealthy !== null && (
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-green-500' : 'bg-red-500'}`}></div>
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {isHealthy ? 'Online' : 'Offline'}
                  </span>
                </div>
              )}
              <button
                onClick={handleClearChat}
                className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
              >
                Clear Chat
              </button>
              <a
                href="/admin"
                className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 text-sm font-medium"
              >
                Admin
              </a>
            </div>
          </div>
        </header>

        {/* Chat Area */}
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto px-4 py-6">
            {messages.length === 0 ? (
              <WelcomeMessage />
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
        <div className="bg-white dark:bg-gray-800">
          <div className="max-w-4xl mx-auto">
            <ChatInput onSend={handleSend} disabled={loading || !isHealthy} />
          </div>
        </div>

        {/* Footer */}
        <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-6 py-3">
          <div className="max-w-7xl mx-auto">
            <p className="text-xs text-center text-gray-500 dark:text-gray-400">
              ⚠️ For educational and research purposes only. Not a substitute for professional medical advice.
            </p>
          </div>
        </footer>
      </div>
    </>
  );
}
