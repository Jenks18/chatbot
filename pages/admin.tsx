import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { apiService, StatsOverview } from '../services/api';

interface SessionInfo {
  session_id: string;
  started_at: string;
  last_active: string;
  message_count: number;
  user_agent: string;
  country?: string;
  city?: string;
  first_message_preview?: string;
}

interface ConversationMessage {
  id: number;
  question: string;
  answer: string;
  created_at: string;
  response_time_ms: number;
  model_used: string;
  ip_address: string;
}

interface SessionHistory {
  session_id: string;
  started_at: string;
  last_active: string;
  user_agent: string;
  country?: string;
  city?: string;
  region?: string;
  timezone?: string;
  latitude?: number;
  longitude?: number;
  message_count: number;
  messages: ConversationMessage[];
}

export default function Admin() {
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [stats, setStats] = useState<StatsOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedSession, setSelectedSession] = useState<SessionHistory | null>(null);
  const [activeTab, setActiveTab] = useState<'sessions' | 'stats'>('sessions');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [sessionsData, statsData] = await Promise.all([
        apiService.getAllSessions(100),
        apiService.getStatsOverview(),
      ]);
      setSessions(sessionsData);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSessionHistory = async (sessionId: string) => {
    try {
      const history = await apiService.getSessionHistory(sessionId);
      setSelectedSession(history);
    } catch (error) {
      console.error('Failed to load session history:', error);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (start: string, end: string) => {
    const diff = new Date(end).getTime() - new Date(start).getTime();
    const minutes = Math.floor(diff / 60000);
    if (minutes < 1) return 'Less than 1 min';
    if (minutes < 60) return `${minutes} min`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h ${minutes % 60}m`;
  };

  return (
    <>
      <Head>
        <title>Admin Dashboard - ToxicoGPT</title>
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
          <div className="max-w-7xl mx-auto flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Admin Dashboard</h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Manage conversations and view analytics
              </p>
            </div>
            <Link
              href="/"
              className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 text-sm font-medium"
            >
              ← Back to Chat
            </Link>
          </div>
        </header>

        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('sessions')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'sessions'
                    ? 'border-toxgreen-600 text-toxgreen-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Conversations ({sessions.length})
              </button>
              <button
                onClick={() => setActiveTab('stats')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'stats'
                    ? 'border-toxgreen-600 text-toxgreen-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Statistics
              </button>
            </nav>
          </div>
        </div>

        <main className="max-w-7xl mx-auto px-6 py-6">
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-toxgreen-600 mx-auto"></div>
              <p className="mt-4 text-gray-600 dark:text-gray-400">Loading...</p>
            </div>
          ) : (
            <>
              {activeTab === 'sessions' && (
                <div className="space-y-4">
                  {sessions.length === 0 ? (
                    <div className="text-center py-12">
                      <p className="text-gray-500 dark:text-gray-400">No conversations yet</p>
                    </div>
                  ) : (
                    sessions.map((session) => (
                      <div
                        key={session.session_id}
                        onClick={() => loadSessionHistory(session.session_id)}
                        className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer border border-gray-200 dark:border-gray-700"
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <span className="text-2xl">💬</span>
                              <div>
                                <h3 className="font-semibold text-gray-900 dark:text-white">
                                  Conversation #{session.session_id.slice(0, 8)}
                                </h3>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                  {session.message_count} message{session.message_count !== 1 ? 's' : ''}
                                </p>
                              </div>
                            </div>
                            {session.first_message_preview && (
                              <p className="text-sm text-gray-600 dark:text-gray-400 italic mb-2">
                                "{session.first_message_preview}..."
                              </p>
                            )}
                            <div className="flex flex-wrap gap-4 text-xs text-gray-500 dark:text-gray-400">
                              <span>🕒 {formatDate(session.started_at)}</span>
                              <span>⏱️ Duration: {formatDuration(session.started_at, session.last_active)}</span>
                              {session.city && session.country && (
                                <span>📍 {session.city}, {session.country}</span>
                              )}
                            </div>
                          </div>
                          <button className="text-toxgreen-600 hover:text-toxgreen-700 text-sm font-medium">
                            View Details →
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}

              {activeTab === 'stats' && stats && (
                <div className="grid gap-6 md:grid-cols-3 mb-8">
                  <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                      Total Queries
                    </h3>
                    <p className="text-3xl font-bold text-gray-900 dark:text-white">
                      {stats.total_queries}
                    </p>
                  </div>
                  <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                      Unique Sessions
                    </h3>
                    <p className="text-3xl font-bold text-gray-900 dark:text-white">
                      {stats.unique_sessions}
                    </p>
                  </div>
                  <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                      Avg Response Time
                    </h3>
                    <p className="text-3xl font-bold text-gray-900 dark:text-white">
                      {stats.avg_response_time_ms.toFixed(0)}ms
                    </p>
                  </div>
                </div>
              )}
            </>
          )}
        </main>
      </div>

      {selectedSession && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
              <div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                  Conversation Details
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Session #{selectedSession.session_id.slice(0, 8)} • {selectedSession.message_count} messages
                </p>
              </div>
              <button
                onClick={() => setSelectedSession(null)}
                className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="px-6 py-4 bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-gray-500 dark:text-gray-400">Started</span>
                  <p className="font-medium text-gray-900 dark:text-white">
                    {formatDate(selectedSession.started_at)}
                  </p>
                </div>
                <div>
                  <span className="text-gray-500 dark:text-gray-400">Duration</span>
                  <p className="font-medium text-gray-900 dark:text-white">
                    {formatDuration(selectedSession.started_at, selectedSession.last_active)}
                  </p>
                </div>
                {selectedSession.city && (
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Location</span>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {selectedSession.city}, {selectedSession.country}
                    </p>
                  </div>
                )}
                {selectedSession.timezone && (
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Timezone</span>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {selectedSession.timezone}
                    </p>
                  </div>
                )}
              </div>
            </div>

            <div className="flex-1 overflow-y-auto px-6 py-4">
              <div className="space-y-6">
                {selectedSession.messages.map((msg, index) => (
                  <div key={msg.id} className="border-l-4 border-toxgreen-500 pl-4">
                    <div className="flex items-start justify-between mb-2">
                      <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
                        Message {index + 1} • {formatDate(msg.created_at)}
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {msg.response_time_ms}ms
                      </span>
                    </div>
                    
                    <div className="mb-3">
                      <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1">
                        USER QUESTION
                      </div>
                      <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3">
                        <p className="text-sm text-gray-900 dark:text-white">{msg.question}</p>
                      </div>
                    </div>

                    <div>
                      <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1">
                        AI RESPONSE
                      </div>
                      <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                        <p className="text-sm text-gray-900 dark:text-white whitespace-pre-wrap">
                          {msg.answer}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end">
              <button
                onClick={() => setSelectedSession(null)}
                className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
