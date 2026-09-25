import React, { createContext, useContext, useState, useCallback } from 'react';
import { chatApi, auditApi } from '../api';
import type { TelemetryEvent, GraphVisualizationPayload } from '../api';

export type RoleType = 'Standard' | 'Analyst' | 'Auditor';

export interface Message {
  id: string;
  sender: 'user' | 'agent';
  text: string;
  telemetry?: TelemetryEvent;
  graph_data?: GraphVisualizationPayload;
  llm_provider?: string;
}

interface ChatContextType {
  messages: Message[];
  loading: boolean;
  error: string | null;
  role: RoleType;
  setRole: (role: RoleType) => void; // switches role AND starts a fresh session

  sendMessage: (text: string) => Promise<void>;
  clearSession: () => void;
  endActiveSession: () => Promise<void>;
  activeGraphData: GraphVisualizationPayload | null;
  setActiveGraphData: (data: GraphVisualizationPayload | null) => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [role, setRole] = useState<RoleType>('Standard');

  const [activeGraphData, setActiveGraphData] = useState<GraphVisualizationPayload | null>(null);

  const sendMessage = useCallback(async (text: string) => {
    const userMessage: Message = { id: Date.now().toString(), sender: 'user', text };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);
    setError(null);

    try {
      const sessionToken = sessionStorage.getItem('aegis_session_token') || undefined;
      const response = await chatApi.sendMessage(text, sessionToken, role);

      // The server renews the ticket on every response; always store the
      // latest one so the session can continue securely.
      sessionStorage.setItem('aegis_session_token', response.session_token);
      sessionStorage.setItem('aegis_session_id', response.session_id);

      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'agent',
        text: response.answer,
        telemetry: response.telemetry,
        graph_data: response.graph_data,
        llm_provider: response.llm_provider,
      };

      setMessages((prev) => [...prev, agentMessage]);
      
      // Auto-visualize the new graph data if it exists
      if (response.graph_data) {
        setActiveGraphData(response.graph_data);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to connect to AegisGraph engine.');
    } finally {
      setLoading(false);
    }
  }, [role]);

  const clearSession = useCallback(() => {
    sessionStorage.removeItem('aegis_session_token');
    sessionStorage.removeItem('aegis_session_id');
    setMessages([]);
    setError(null);
    setActiveGraphData(null);
  }, []);

  // Changing role mid-conversation isn't allowed server-side (the role is
  // locked into the session ticket at creation time) — so switching roles
  // here intentionally starts a fresh, zero-risk session under the new role.
  const changeRole = useCallback((newRole: RoleType) => {
    setRole(newRole);
    clearSession();
  }, [clearSession]);

  const endActiveSession = useCallback(async () => {
    const sessionId = sessionStorage.getItem('aegis_session_id');
    if (sessionId) {
      try {
        await auditApi.endSession(sessionId);
      } catch (err) {
        console.error('Failed to end session on backend', err);
      }
      clearSession();
    }
  }, [clearSession]);

  return (
    <ChatContext.Provider value={{
      messages, loading, error, role, setRole: changeRole,
      sendMessage, clearSession, endActiveSession,
      activeGraphData, setActiveGraphData
    }}>
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
}
