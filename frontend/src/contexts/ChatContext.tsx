import React, { createContext, useContext, useState, useCallback } from 'react';
import { chatApi, auditApi } from '../api';
import type { TelemetryEvent, GraphVisualizationPayload, LLMProviderType } from '../api';

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
  setRole: (role: RoleType) => void;
  llmProvider: LLMProviderType;
  setLlmProvider: (provider: LLMProviderType) => void;
  sendMessage: (text: string) => Promise<void>;
  clearSession: () => void;
  endActiveSession: () => Promise<void>;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [role, setRole] = useState<RoleType>('Standard');
  const [llmProvider, setLlmProvider] = useState<LLMProviderType>('ollama');

  const sendMessage = useCallback(async (text: string) => {
    const userMessage: Message = { id: Date.now().toString(), sender: 'user', text };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);
    setError(null);

    try {
      const sessionId = sessionStorage.getItem('aegis_session_id') || undefined;
      const response = await chatApi.sendMessage(text, sessionId, role, llmProvider);
      
      if (!sessionId) {
        sessionStorage.setItem('aegis_session_id', response.session_id);
      }

      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'agent',
        text: response.answer,
        telemetry: response.telemetry,
        graph_data: response.graph_data,
        llm_provider: response.llm_provider,
      };

      setMessages((prev) => [...prev, agentMessage]);
    } catch (err: any) {
      setError(err.message || 'Failed to connect to AegisGraph engine.');
    } finally {
      setLoading(false);
    }
  }, [role, llmProvider]);

  const clearSession = useCallback(() => {
    sessionStorage.removeItem('aegis_session_id');
    setMessages([]);
    setError(null);
  }, []);

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
    <ChatContext.Provider value={{ messages, loading, error, role, setRole, llmProvider, setLlmProvider, sendMessage, clearSession, endActiveSession }}>
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
