import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { apiService, ChatLog, StatsOverview } from '../services/api';

export default function Admin() {
  const [logs, setLogs] = useState<ChatLog[]>([]);
  const [stats, setStats] = useState<StatsOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'logs' | 'stats'>('logs');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [logsData, statsData] = await Promise.all([
        apiService.getRecentLogs(24, 100),
        apiService.getStatsOverview(),
      ]);
      setLogs(logsData);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadData();
      return;
    }
    setLoading(true);
    try {
      const results = await apiService.searchLogs(searchQuery);
      setLogs(results);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <>
      <Head>
        <title>Admin Dashboard - ToxicoGPT</title>
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        {/* Header */}
        <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
          <div className="max-w-7xl mx-auto flex justify-between items-center">
            <div className="flex items-center gap-3">
              <span className="text-3xl">📊</span>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Admin Dashboard</h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">View and analyze chat interactions</p>
              </div>
            </div>
            <Link href="/" className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
              Back to Chat
            </Link>
          </div>
        </header>

        {/* Tabs */}
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <div className="max-w-7xl mx-auto px-6">
            <div className="flex gap-6">
              <button
                onClick={() => setActiveTab('stats')}
                className={`py-3 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'stats'
                    ? 'border-primary-600 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Statistics
              </button>
              <button
                onClick={() => setActiveTab('logs')}
                className={`py-3 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'logs'
                    ? 'border-primary-600 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Chat Logs
              </button>
            </div>
          </div>
        </div>

        {/* Content */}
        <main className="max-w-7xl mx-auto px-6 py-8">
          {activeTab === 'stats' && stats && (
            <div className="space-y-6">
              {/* Stats Cards */}
              <div className="grid md:grid-cols-3 gap-6">
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Total Queries</p>
                      <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                        {stats.total_queries}
                      </p>
                    </div>
                    <div className="text-4xl">💬</div>
                  </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Unique Sessions</p>
                      <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                        {stats.unique_sessions}
                      </p>
                    </div>
                    <div className="text-4xl">👥</div>
                  </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Avg Response Time</p>
                      <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                        {stats.avg_response_time_ms.toFixed(0)}ms
                      </p>
                    </div>
                    <div className="text-4xl">⚡</div>
                  </div>
                </div>
              </div>

              {/* Daily Queries Chart */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Daily Query Volume (Last 7 Days)
                </h3>
                <div className="space-y-2">
                  {stats.daily_queries.map((day) => (
                    <div key={day.date} className="flex items-center gap-4">
                      <div className="w-24 text-sm text-gray-600 dark:text-gray-400">{day.date}</div>
                      <div className="flex-1">
                        <div className="bg-gray-200 dark:bg-gray-700 rounded-full h-6 overflow-hidden">
                          <div
                            className="bg-primary-600 h-full flex items-center px-2"
                            style={{ width: `${Math.min((day.count / Math.max(...stats.daily_queries.map(d => d.count))) * 100, 100)}%` }}
                          >
                            <span className="text-xs text-white font-medium">{day.count}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'logs' && (
            <div className="space-y-6">
              {/* Search */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                    placeholder="Search in questions and answers..."
                    className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
                  />
                  <button
                    onClick={handleSearch}
                    className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                  >
                    Search
                  </button>
                  <button
                    onClick={loadData}
                    className="px-6 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600"
                  >
                    Refresh
                  </button>
                </div>
              </div>

              {/* Logs Table */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 dark:bg-gray-700">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Time</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Location</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">IP Address</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Question</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Answer</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Response Time</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                      {loading ? (
                        <tr>
                          <td colSpan={6} className="px-4 py-8 text-center text-gray-500">Loading...</td>
                        </tr>
                      ) : logs.length === 0 ? (
                        <tr>
                          <td colSpan={6} className="px-4 py-8 text-center text-gray-500">No logs found</td>
                        </tr>
                      ) : (
                        logs.map((log) => {
                          const geoData = log.extra_metadata?.geo_data;
                          const location = geoData ? 
                            [geoData.city, geoData.region, geoData.country].filter(Boolean).join(', ') || 'Unknown' 
                            : 'Unknown';
                          
                          return (
                            <tr key={log.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                              <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400 whitespace-nowrap">
                                {formatDate(log.created_at)}
                              </td>
                              <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">
                                <div className="flex items-center gap-1">
                                  <span>📍</span>
                                  <span className="max-w-xs truncate" title={location}>{location}</span>
                                </div>
                                {geoData?.timezone && (
                                  <div className="text-xs text-gray-500">{geoData.timezone}</div>
                                )}
                              </td>
                              <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400 font-mono whitespace-nowrap">
                                {log.ip_address || 'N/A'}
                              </td>
                              <td className="px-4 py-3 text-sm text-gray-900 dark:text-white max-w-md">
                                <div className="truncate" title={log.question}>{log.question}</div>
                              </td>
                              <td className="px-4 py-3 text-sm text-gray-900 dark:text-white max-w-md">
                                <div className="truncate" title={log.answer}>{log.answer}</div>
                              </td>
                              <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400 whitespace-nowrap">
                                {log.response_time_ms}ms
                              </td>
                            </tr>
                          );
                        })
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </>
  );
}
