import axios from 'axios';

// Use environment variable or fallback to localhost for development
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ChatMessage {
  message: string;
  session_id?: string;
}

export interface ChatResponse {
  answer: string;
  session_id: string;
  model_used: string;
  response_time_ms: number;
  sources?: string[];
}

export interface ChatLog {
  id: number;
  session_id: string;
  question: string;
  answer: string;
  model_used: string | null;
  response_time_ms: number | null;
  ip_address?: string;
  user_agent?: string;
  created_at: string;
  extra_metadata?: {
    geo_data?: {
      country?: string;
      city?: string;
      region?: string;
      timezone?: string;
      lat?: string;
      lon?: string;
      isp?: string;
    };
    rag_used?: boolean;
  };
}

export interface SessionStats {
  session_id: string;
  message_count: number;
  started_at: string | null;
  last_active: string | null;
}

export interface HealthStatus {
  status: string;
  database: string;
  model_server: string;
  timestamp: string;
}

export interface StatsOverview {
  total_queries: number;
  unique_sessions: number;
  avg_response_time_ms: number;
  daily_queries: Array<{ date: string; count: number }>;
}

class ApiService {
  private baseURL: string;

  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Chat endpoints
  async sendMessage(message: string, sessionId?: string): Promise<ChatResponse> {
    const response = await axios.post<ChatResponse>(`${this.baseURL}/api/chat`, {
      message,
      session_id: sessionId,
    });
    return response.data;
  }

  async getChatHistory(sessionId: string, limit: number = 50): Promise<{ session_id: string; history: ChatLog[] }> {
    const response = await axios.get(`${this.baseURL}/api/history/${sessionId}`, {
      params: { limit },
    });
    return response.data;
  }

  async getSessionStats(sessionId: string): Promise<SessionStats> {
    const response = await axios.get(`${this.baseURL}/api/session/${sessionId}/stats`);
    return response.data;
  }

  // Admin endpoints
  async getAllLogs(limit: number = 100, offset: number = 0): Promise<ChatLog[]> {
    const response = await axios.get<ChatLog[]>(`${this.baseURL}/api/admin/logs`, {
      params: { limit, offset },
    });
    return response.data;
  }

  async getRecentLogs(hours: number = 24, limit: number = 100): Promise<ChatLog[]> {
    const response = await axios.get<ChatLog[]>(`${this.baseURL}/api/admin/logs/recent`, {
      params: { hours, limit },
    });
    return response.data;
  }

  async getStatsOverview(): Promise<StatsOverview> {
    const response = await axios.get<StatsOverview>(`${this.baseURL}/api/admin/stats/overview`);
    return response.data;
  }

  async getAllSessions(limit: number = 50): Promise<any[]> {
    const response = await axios.get(`${this.baseURL}/api/admin/sessions`, {
      params: { limit },
    });
    return response.data;
  }

  async getSessionHistory(sessionId: string): Promise<any> {
    const response = await axios.get(`${this.baseURL}/api/admin/sessions/${sessionId}/history`);
    return response.data;
  }

  async searchLogs(query: string, limit: number = 50): Promise<ChatLog[]> {
    const response = await axios.get<ChatLog[]>(`${this.baseURL}/api/admin/search`, {
      params: { query, limit },
    });
    return response.data;
  }

  // Health check
  async checkHealth(): Promise<HealthStatus> {
    const response = await axios.get<HealthStatus>(`${this.baseURL}/health`);
    return response.data;
  }
}

export const apiService = new ApiService();
