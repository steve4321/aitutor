'use client';

import { create } from 'zustand';
import type { ChatMessage } from '@/types/problem';

interface AppState {
  sidebarOpen: boolean;
  activeChatMessages: ChatMessage[];
  currentLessonId: string | null;
  currentCourseId: string | null;

  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setActiveChatMessages: (messages: ChatMessage[]) => void;
  addChatMessage: (message: ChatMessage) => void;
  clearChatMessages: () => void;
  setCurrentLesson: (courseId: string | null, lessonId: string | null) => void;
}

export const useAppStore = create<AppState>()((set) => ({
  sidebarOpen: false,
  activeChatMessages: [],
  currentLessonId: null,
  currentCourseId: null,

  toggleSidebar: () =>
    set((state) => ({ sidebarOpen: !state.sidebarOpen })),

  setSidebarOpen: (sidebarOpen) =>
    set({ sidebarOpen }),

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
