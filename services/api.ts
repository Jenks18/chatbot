import axios from 'axios';

// For Vercel deployment, use relative path so frontend and backend are on same domain
// For local development, use localhost:8000
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 
  (typeof window !== 'undefined' && window.location.hostname !== 'localhost' 
    ? '' // Use relative path in production (Vercel)
    : 'http://localhost:8000'); // Use localhost in development

export interface ChatMessage {
  message: string;
  session_id?: string;
  user_mode?: 'patient' | 'doctor' | 'researcher';
}

export interface ChatResponse {
  answer: string;
  session_id: string;
  model_used: string;
  response_time_ms: number;
  consumer_summary?: string;
  sources?: string[];
  evidence?: Array<{
    id: number;
    drug_name: string;
    title?: string;
    summary: string;
    mechanism?: string;
    food_groups?: string[];
    recommended_actions?: string;
    evidence_quality?: string;
    references?: Array<{ id: number; title: string; url: string; excerpt?: string }>;
  }>;
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
  async sendMessage(message: string, sessionId?: string, userMode?: 'patient' | 'doctor' | 'researcher'): Promise<ChatResponse> {
    const endpoint = this.baseURL ? `${this.baseURL}/api/chat` : '/api/chat';
    const response = await axios.post<ChatResponse>(endpoint, {
      message,
      session_id: sessionId,
      user_mode: userMode || 'patient',
    });
    return response.data;
  }

  async getChatHistory(sessionId: string, limit: number = 50): Promise<{ session_id: string; history: ChatLog[] }> {
    const endpoint = this.baseURL ? `${this.baseURL}/api/history/${sessionId}` : `/api/history/${sessionId}`;
    const response = await axios.get(endpoint, {
      params: { limit },
    });
    return response.data;
  }

  async getSessionStats(sessionId: string): Promise<SessionStats> {
    const endpoint = this.baseURL ? `${this.baseURL}/api/session/${sessionId}/stats` : `/api/session/${sessionId}/stats`;
    const response = await axios.get(endpoint);
    return response.data;
  }

  // Admin endpoints
  async getAllLogs(limit: number = 100, offset: number = 0): Promise<ChatLog[]> {
    const endpoint = this.baseURL ? `${this.baseURL}/api/admin/logs` : '/api/admin/logs';
    const response = await axios.get<ChatLog[]>(endpoint, {
      params: { limit, offset },
    });
    return response.data;
  }

  async getRecentLogs(hours: number = 24, limit: number = 100): Promise<ChatLog[]> {
    const endpoint = this.baseURL ? `${this.baseURL}/api/admin/logs/recent` : '/api/admin/logs/recent';
    const response = await axios.get<ChatLog[]>(endpoint, {
      params: { hours, limit },
    });
    return response.data;
  }

  async getStatsOverview(): Promise<StatsOverview> {
    const endpoint = this.baseURL ? `${this.baseURL}/api/admin/stats/overview` : '/api/admin/stats/overview';
    const response = await axios.get<StatsOverview>(endpoint);
    return response.data;
  }

  async getAllSessions(limit: number = 50): Promise<any[]> {
    const endpoint = this.baseURL ? `${this.baseURL}/api/admin/sessions` : '/api/admin/sessions';
    const response = await axios.get(endpoint, {
      params: { limit },
    });
    return response.data;
  }

  // Interaction management
  async getInteractions(limit: number = 100): Promise<any[]> {
    const endpoint = this.baseURL ? `${this.baseURL}/api/admin/interactions` : '/api/admin/interactions';
    const response = await axios.get(endpoint, {
      params: { limit },
    });
    return response.data;
  }

  async runFetchReferences(limit: number = 100): Promise<any> {
    const endpoint = this.baseURL ? `${this.baseURL}/api/admin/pipeline/fetch-references` : '/api/admin/pipeline/fetch-references';
    const response = await axios.post(endpoint, null, {
      params: { limit },
    });
    return response.data;
  }

  async getSessionHistory(sessionId: string): Promise<any> {
    const endpoint = this.baseURL ? `${this.baseURL}/api/admin/sessions/${sessionId}/history` : `/api/admin/sessions/${sessionId}/history`;
    const response = await axios.get(endpoint);
    return response.data;
  }

  async searchLogs(query: string, limit: number = 50): Promise<ChatLog[]> {
    const endpoint = this.baseURL ? `${this.baseURL}/api/admin/search` : '/api/admin/search';
    const response = await axios.get<ChatLog[]>(endpoint, {
      params: { query, limit },
    });
    return response.data;
  }

  // Health check
  async checkHealth(): Promise<HealthStatus> {
    const endpoint = this.baseURL ? `${this.baseURL}/health` : '/api/health';
    const response = await axios.get<HealthStatus>(endpoint);
    return response.data;
  }
}

export const apiService = new ApiService();
