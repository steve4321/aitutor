'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
import { api } from '@/lib/api';
import type { ChatMessageResponse } from '@/types/problem';

export interface ChatMessage extends Omit<ChatMessageResponse, 'session_id'> {
  timestamp: string;
}

interface UseChatOptions {
  sessionId?: string | null;
  autoCreate?: boolean;
  subject?: string;
}

interface UseChatReturn {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sessionId: string | null;
  send: (content: string) => Promise<void>;
  clear: () => void;
  reload: () => Promise<void>;
}

export function useChat(options: UseChatOptions = {}): UseChatReturn {
  const { sessionId: initialSessionId, autoCreate = true, subject = 'math' } = options;
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(
    initialSessionId ?? null
  );
  const inFlightRef = useRef(false);

  const send = useCallback(
    async (content: string) => {
      if (!content.trim() || inFlightRef.current) return;
      inFlightRef.current = true;
      setIsLoading(true);
      setError(null);

      const tempUserMsg: ChatMessage = {
        id: `temp-${Date.now()}`,
        role: 'user',
        content: content.trim(),
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, tempUserMsg]);

      try {
        const body: { content: string; session_id?: string } = {
          content: content.trim(),
        };
        if (sessionId) body.session_id = sessionId;

        const response = await api.post<{
          id: string;
          role: string;
          content: string;
          session_id: string;
        }>('/chat/message', body);

        if (!sessionId) setSessionId(response.session_id);

        const aiMsg: ChatMessage = {
          id: response.id,
          role: 'assistant',
          content: response.content,
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, aiMsg]);
      } catch (err) {
        const errorMsg =
          err instanceof Error ? err.message : '发送失败，请重试';
        setError(errorMsg);
        setMessages((prev) => prev.filter((m) => m.id !== tempUserMsg.id));
      } finally {
        setIsLoading(false);
        inFlightRef.current = false;
      }
    },
    [sessionId]
  );

  const clear = useCallback(() => {
    setMessages([]);
    setError(null);
    setSessionId(null);
  }, []);

  const reload = useCallback(async () => {
    if (!sessionId) return;
    try {
      const session = await api.get<{ messages: ChatMessage[] }>(
        `/sessions/${sessionId}`
      );
      setMessages(session.messages || []);
    } catch (err) {
      console.warn('[useChat] Failed to reload session messages:', err);
    }
  }, [sessionId]);

  useEffect(() => {
    if (autoCreate && !sessionId) {
      api
        .post<{ id: string }>('/sessions', {
          session_type: 'chat',
          subject,
        })
        .then((data) => setSessionId(data.id))
        .catch((err) => {
          console.warn('[useChat] Auto-create session failed, will create on first message:', err);
        });
    }
  }, [autoCreate, sessionId]);

  return { messages, isLoading, error, sessionId, send, clear, reload };
}
