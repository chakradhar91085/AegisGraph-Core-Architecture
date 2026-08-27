import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

export type LLMProviderType = 'gemini' | 'ollama';

export interface AdaptivePolicy {
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  attenuation_factor: number;
  effective_context_limit: number;
  effective_graph_depth: number;
  response_mode: 'ALLOW' | 'MASK' | 'RESTRICT' | 'BLOCK';
}

export interface SignalValues {
  semantic_drift: number;
  temporal_frequency: number;
  entity_focus: number;
  graph_footprint: number;
}

export interface TelemetryEvent {
  session_id: string;
  timestamp: number;
  query: string;
  intent: string;
  retrieval_strategy: string;
  result_count: number;
  signals: SignalValues;
  instantaneous_risk: number;
  smoothed_risk: number;
  policy: AdaptivePolicy;
  blocked_by_policy: boolean;
  role: string;
  response_mode: 'ALLOW' | 'MASK' | 'RESTRICT' | 'BLOCK';
}

export interface ChatRequest {
  query: string;
  session_id?: string;
  role?: string;
  llm_provider?: LLMProviderType;
}

export interface GraphNode {
  id: string;
  label: string;
  type: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
  weight?: number;
}

export interface GraphVisualizationPayload {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface ChatResponse {
  answer: string;
  session_id: string;
  intent: string;
  retrieval: {
    result_count: number;
    strategy: string;
  };
  status: string;
  telemetry: TelemetryEvent;
  graph_data?: GraphVisualizationPayload;
  llm_provider?: string;
}

export const chatApi = {
  async sendMessage(
    query: string,
    sessionId?: string,
    role: string = 'Standard',
    llmProvider?: LLMProviderType
  ): Promise<ChatResponse> {
    const payload: ChatRequest = { query, role };
    if (sessionId) {
      payload.session_id = sessionId;
    }
    if (llmProvider) {
      payload.llm_provider = llmProvider;
    }
    const response = await axios.post<ChatResponse>(`${API_BASE}/chat`, payload);
    return response.data;
  },
};

export interface AuditSession {
  session_id: string;
  role: string;
  started_at: string;
  ended_at: string | null;
  status: string;
  query_count: number;
  final_risk_score: number;
  peak_risk_score: number;
  final_behavioral_mode: string;
  highest_behavioral_mode: string;
}

export interface AuditQuery {
  id: string;
  timestamp: string;
  query: string;
  intent: string;
  risk_score: number;
  behavioral_mode: string;
  retrieval_outcome: string;
  masked: boolean;
  attenuated: boolean;
  blocked: boolean;
  result_count: number;
  role: string;
  llm_provider: string;
}

export const auditApi = {
  async getAuditLogs(limit: number = 100): Promise<TelemetryEvent[]> {
    const response = await axios.get<{logs: TelemetryEvent[]}>(`${API_BASE}/audit?limit=${limit}`);
    return response.data.logs;
  },
  
  async getSessions(limit: number = 50): Promise<AuditSession[]> {
    const response = await axios.get<{sessions: AuditSession[]}>(`${API_BASE}/audit/sessions?limit=${limit}`);
    return response.data.sessions;
  },
  
  async getSessionQueries(sessionId: string): Promise<AuditQuery[]> {
    const response = await axios.get<{queries: AuditQuery[]}>(`${API_BASE}/audit/sessions/${sessionId}/queries`);
    return response.data.queries;
  },
  
  async endSession(sessionId: string): Promise<void> {
    await axios.post(`${API_BASE}/audit/sessions/${sessionId}/end`);
  }
};
