'use client';

import { useState, useCallback } from 'react';
import { api } from '@/lib/api';
import { useAppStore } from '@/stores/app-store';
import type { ChatMessage } from '@/types/problem';

export function useChat(sessionId?: string) {
  const { activeChatMessages, addChatMessage, clearChatMessages } = useAppStore();
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = useCallback(
    async (content: string) => {
      const userMessage: ChatMessage = {
        id: `temp-${Date.now()}`,
        role: 'user',
        content,
        timestamp: new Date().toISOString(),
      };
      addChatMessage(userMessage);

      setIsLoading(true);
      try {
        const response = await api.post<ChatMessage>('/chat/message', {
          session_id: sessionId,
          content,
        });
        addChatMessage(response);
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId, addChatMessage]
  );

  const resetChat = useCallback(() => {
    clearChatMessages();
  }, [clearChatMessages]);

  return {
    messages: activeChatMessages,
    isLoading,
    sendMessage,
    resetChat,
  };
}
