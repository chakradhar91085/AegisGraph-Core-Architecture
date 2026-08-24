import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

export interface AdaptivePolicy {
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  attenuation_factor: number;
  effective_context_limit: number;
  effective_graph_depth: number;
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
}

export interface ChatRequest {
  query: string;
  session_id?: string;
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
}

export const chatApi = {
  async sendMessage(query: string, sessionId?: string): Promise<ChatResponse> {
    const payload: ChatRequest = { query };
    if (sessionId) {
      payload.session_id = sessionId;
    }
    const response = await axios.post<ChatResponse>(`${API_BASE}/chat`, payload);
    return response.data;
  },
};
