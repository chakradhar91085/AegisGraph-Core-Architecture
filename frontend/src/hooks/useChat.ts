import { useState, useCallback } from 'react';
import { chatApi } from '../api';
import type { TelemetryEvent, GraphVisualizationPayload } from '../api';

export interface Message {
  id: string;
  sender: 'user' | 'agent';
  text: string;
  telemetry?: TelemetryEvent;
  graph_data?: GraphVisualizationPayload;
}

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (text: string) => {
    const userMessage: Message = { id: Date.now().toString(), sender: 'user', text };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);
    setError(null);

    try {
      const sessionId = sessionStorage.getItem('aegis_session_id') || undefined;
      const response = await chatApi.sendMessage(text, sessionId);
      
      if (!sessionId) {
        sessionStorage.setItem('aegis_session_id', response.session_id);
      }

      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'agent',
        text: response.answer,
        telemetry: response.telemetry,
        graph_data: response.graph_data,
      };

      setMessages((prev) => [...prev, agentMessage]);
    } catch (err: any) {
      setError(err.message || 'Failed to send message');
    } finally {
      setLoading(false);
    }
  }, []);

  const clearSession = useCallback(() => {
    sessionStorage.removeItem('aegis_session_id');
    setMessages([]);
    setError(null);
  }, []);

  return { messages, loading, error, sendMessage, clearSession };
}
