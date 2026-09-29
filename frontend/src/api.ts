import axios from 'axios';

const API_BASE = 'http://localhost:8001/api/v1';

// Every request carries the signed-in user's Clerk session token; the backend
// verifies it and decides the user's role. Nothing here can choose a role.
let tokenGetter: (() => Promise<string | null>) | null = null;
export const setTokenGetter = (getter: () => Promise<string | null>) => {
  tokenGetter = getter;
};
axios.interceptors.request.use(async (config) => {
  const token = tokenGetter ? await tokenGetter() : null;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export interface AdaptivePolicy {
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  attenuation_factor: number;
  effective_context_limit: number;
  effective_graph_depth: number;
  response_mode: 'ALLOW' | 'MASK' | 'RESTRICT' | 'BLOCK';
}

export interface SignalValues {
  semantic_focus: number;
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
  session_token?: string;
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
  session_token: string;
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
    sessionToken?: string,
  ): Promise<ChatResponse> {
    const payload: ChatRequest = { query };
    if (sessionToken) {
      payload.session_token = sessionToken;
    }
    const response = await axios.post<ChatResponse>(`${API_BASE}/chat`, payload);
    return response.data;
  },

  async me(): Promise<{ user_id: string; role: string }> {
    return (await axios.get(`${API_BASE}/me`)).data;
  },

  async endSession(sessionToken: string): Promise<void> {
    await axios.post(`${API_BASE}/session/end`, { session_token: sessionToken });
  },

  // Only takes effect when the server runs with DEMO_ALLOW_RISK_RESET=true.
  async resetRisk(): Promise<void> {
    await axios.post(`${API_BASE}/session/reset`);
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
  async getSessions(limit: number = 50): Promise<AuditSession[]> {
    const response = await axios.get<{sessions: AuditSession[]}>(`${API_BASE}/audit/sessions?limit=${limit}`);
    return response.data.sessions;
  },
  
  async getSessionQueries(sessionId: string): Promise<AuditQuery[]> {
    const response = await axios.get<{queries: AuditQuery[]}>(`${API_BASE}/audit/sessions/${sessionId}/queries`);
    return response.data.queries;
  },
};
