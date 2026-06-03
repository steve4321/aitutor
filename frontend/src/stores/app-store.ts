'use client';

import { create } from 'zustand';
import type { ChatMessage } from '@/types/problem';

interface AppState {
  activeChatMessages: ChatMessage[];
  currentLessonId: string | null;
  currentCourseId: string | null;

  setActiveChatMessages: (messages: ChatMessage[]) => void;
  addChatMessage: (message: ChatMessage) => void;
  clearChatMessages: () => void;
  setCurrentLesson: (courseId: string | null, lessonId: string | null) => void;
}

export const useAppStore = create<AppState>()((set) => ({
  activeChatMessages: [],
  currentLessonId: null,
  currentCourseId: null,

  setActiveChatMessages: (activeChatMessages) =>
    set({ activeChatMessages }),

  addChatMessage: (message) =>
    set((state) => ({
      activeChatMessages: [...state.activeChatMessages, message],
    })),

  clearChatMessages: () =>
    set({ activeChatMessages: [] }),

  setCurrentLesson: (currentCourseId, currentLessonId) =>
    set({ currentCourseId, currentLessonId }),
}));
