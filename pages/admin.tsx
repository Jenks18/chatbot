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
  const [interactions, setInteractions] = useState<any[]>([]);
  const [pipelineResult, setPipelineResult] = useState<any | null>(null);
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
        // note: interactions fetched separately to keep initial load fast
      ]);
      
      // Ensure sessionsData is an array and filter out invalid entries
      const validSessions = Array.isArray(sessionsData) 
        ? sessionsData.filter(s => s && s.session_id) 
        : [];
      
      setSessions(validSessions);
      setStats(statsData || null);
      loadInteractions();
    } catch (error) {
      console.error('Failed to load admin data:', error);
      setSessions([]);
      setStats(null);
    } finally {
      setLoading(false);
    }
  };

  const loadInteractions = async () => {
    try {
      const data = await apiService.getInteractions(200);
      setInteractions(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Failed to load interactions', err);
      setInteractions([]);
    }
  };

  const runPipeline = async () => {
    try {
      setPipelineResult(null);
      const res = await apiService.runFetchReferences(200);
      setPipelineResult(res);
      // reload interactions to show excerpts
      loadInteractions();
    } catch (err) {
      console.error('Pipeline failed', err);
    }
  };

  const loadSessionHistory = async (sessionId: string) => {
    try {
      const history = await apiService.getSessionHistory(sessionId);
      
      // Validate the response
      if (!history || !history.session_id) {
        console.error('Invalid session history response:', history);
        alert('Failed to load session history: Invalid response from server');
        return;
      }
      
      // Ensure messages array exists
      if (!history.messages) {
        history.messages = [];
      }
      
      setSelectedSession(history);
    } catch (error) {
      console.error('Failed to load session history:', error);
      alert('Failed to load session history. Please try again.');
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
        <title>Admin Dashboard - Kandih ToxWiki</title>
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
          <div className="max-w-7xl mx-auto flex justify-between items-center">
            <div className="flex items-center gap-3">
              <span className="text-3xl">🧬</span>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Kandih ToxWiki — Admin</h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">Manage conversations, interactions, and reference data</p>
              </div>
            </div>
            <div className="flex gap-3">
              <button
                onClick={loadData}
                className="px-4 py-2 bg-toxgreen-600 text-white rounded-lg hover:bg-toxgreen-700 text-sm font-medium flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Refresh
              </button>
              <button
                onClick={runPipeline}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M8 12l4-4 4 4M12 8v8" />
                </svg>
                Fetch & Update References
              </button>
              <Link
                href="/"
                className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 text-sm font-medium"
              >
                ← Back to Chat
              </Link>
            </div>
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
                    sessions.filter(session => session && session.session_id).map((session) => (
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
                                  Conversation #{session.session_id?.slice(0, 8) || 'unknown'}
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
                          <div className="text-toxgreen-600 hover:text-toxgreen-700 text-sm font-medium pointer-events-none">
                            View Details →
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}

              {activeTab === 'stats' && (
                <div className="mb-8">
                  <h3 className="text-lg font-semibold mb-3">Manage Interactions</h3>
                  <div className="grid gap-4">
                    {interactions && interactions.length > 0 ? (
                      interactions.map((it) => (
                        <div key={it.id} className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="font-semibold">{it.title || it.drug_name}</div>
                              <div className="text-xs text-gray-500 dark:text-gray-400">Drug: {it.drug_name}</div>
                              <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">{it.summary}</p>
                            </div>
                            <div className="text-right">
                              <div className="text-xs text-gray-500">Evidence: {it.evidence_quality}</div>
                              <div className="mt-2">
                                {it.references && it.references.length > 0 && it.references.map((r: any) => (
                                  <div key={r.id} className="text-xs">
                                    <a href={r.url} target="_blank" rel="noreferrer" className="text-indigo-600 hover:underline">{r.title}</a>
                                    {r.excerpt && <div className="text-gray-500 text-xs mt-1 max-w-xs">{r.excerpt.slice(0,140)}{r.excerpt.length>140? '…':''}</div>}
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                        No interactions found
                      </div>
                    )}
                  </div>

                  {pipelineResult && (
                    <div className="mt-6 bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                      <div className="font-medium">Pipeline Result</div>
                      <pre className="text-xs mt-2 text-gray-600 dark:text-gray-300">{JSON.stringify(pipelineResult, null, 2)}</pre>
                    </div>
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
                  Session #{selectedSession.session_id?.slice(0, 8) || 'unknown'} • {selectedSession.message_count} messages
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
                {selectedSession.messages && selectedSession.messages.length > 0 ? (
                  selectedSession.messages.map((msg, index) => (
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
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                    No messages found for this session
                  </div>
                )}
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
