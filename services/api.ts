import axios from 'axios';

// For Vercel deployment, use relative path so frontend and backend are on same domain
// For local development, use localhost:8000
const IS_PRODUCTION = typeof window !== 'undefined' && window.location.hostname !== 'localhost';
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 
  (IS_PRODUCTION ? '' : 'http://localhost:8000');

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
    evidence?: Array<any>;
    consumer_summary?: string;
    consumer_summary_provenance?: {
      source: string;
      evidence_ids?: number[];
    };
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
  private isProduction: boolean;

  constructor() {
    this.baseURL = API_BASE_URL;
    this.isProduction = IS_PRODUCTION;
  }

  // Helper to build endpoint URL
  private buildEndpoint(path: string): string {
    // In production (Vercel), paths are already at /api/*
    // In development, prefix with baseURL
    return this.isProduction ? path : `${this.baseURL}${path}`;
  }

  // Chat endpoints
  async sendMessage(message: string, sessionId?: string, userMode?: 'patient' | 'doctor' | 'researcher'): Promise<ChatResponse> {
    const response = await axios.post<ChatResponse>(this.buildEndpoint('/api/chat'), {
      message,
      session_id: sessionId,
      user_mode: userMode || 'patient',
    });
    return response.data;
  }

  async getChatHistory(sessionId: string, limit: number = 50): Promise<{ session_id: string; history: ChatLog[] }> {
    const response = await axios.get(this.buildEndpoint(`/api/history/${sessionId}`), {
      params: { limit },
    });
    return response.data;
  }

  async getSessionStats(sessionId: string): Promise<SessionStats> {
    const response = await axios.get(this.buildEndpoint(`/api/session/${sessionId}/stats`));
    return response.data;
  }

  // Admin endpoints
  async getAllLogs(limit: number = 100, offset: number = 0): Promise<ChatLog[]> {
    const response = await axios.get<ChatLog[]>(this.buildEndpoint('/api/admin/logs'), {
      params: { limit, offset },
    });
    return response.data;
  }

  async getRecentLogs(hours: number = 24, limit: number = 100): Promise<ChatLog[]> {
    const response = await axios.get<ChatLog[]>(this.buildEndpoint('/api/admin/logs/recent'), {
      params: { hours, limit },
    });
    return response.data;
  }

  async getStatsOverview(): Promise<StatsOverview> {
    const response = await axios.get<StatsOverview>(this.buildEndpoint('/api/admin/stats/overview'));
    return response.data;
  }

  async getAllSessions(limit: number = 50): Promise<any[]> {
    const response = await axios.get(this.buildEndpoint('/api/admin/sessions'), {
      params: { limit },
    });
    return response.data;
  }

  // Interaction management
  async getInteractions(limit: number = 100): Promise<any[]> {
    const response = await axios.get(this.buildEndpoint('/api/admin/interactions'), {
      params: { limit },
    });
    return response.data;
  }

  async runFetchReferences(limit: number = 100): Promise<any> {
    const response = await axios.post(this.buildEndpoint('/api/admin/pipeline/fetch-references'), null, {
      params: { limit },
    });
    return response.data;
  }

  async getSessionHistory(sessionId: string): Promise<any> {
    const response = await axios.get(this.buildEndpoint(`/api/admin/sessions/${sessionId}/history`));
    return response.data;
  }

  async searchLogs(query: string, limit: number = 50): Promise<ChatLog[]> {
    const response = await axios.get<ChatLog[]>(this.buildEndpoint('/api/admin/search'), {
      params: { query, limit },
    });
    return response.data;
  }

  // Health check
  async checkHealth(): Promise<HealthStatus> {
    const response = await axios.get<HealthStatus>(this.buildEndpoint('/api/health'));
    return response.data;
  }
}

export const apiService = new ApiService();
