import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { useChat } from '../use-chat';
import { api } from '@/lib/api';

vi.mock('@/lib/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

describe('useChat', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns correct initial state', () => {
    const { result } = renderHook(() => useChat({ autoCreate: false }));

    expect(result.current.messages).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.sessionId).toBeNull();
  });

  it('auto-creates a session when autoCreate is true', async () => {
    (api.post as ReturnType<typeof vi.fn>).mockResolvedValueOnce({ id: 'session-1' });

    renderHook(() => useChat({ autoCreate: true }));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/sessions', {
        session_type: 'chat',
        subject: 'math',
      });
    });
  });

  it('does not auto-create session when autoCreate is false', () => {
    renderHook(() => useChat({ autoCreate: false }));

    expect(api.post).not.toHaveBeenCalledWith('/sessions', expect.any(Object));
  });

  it('sends a message and receives AI response', async () => {
    (api.post as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      id: 'msg-ai-1',
      role: 'assistant',
      content: 'Hello!',
      session_id: 'session-1',
    });

    const { result } = renderHook(() => useChat({ autoCreate: false }));

    await act(async () => {
      await result.current.send('Hi there');
    });

    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[0].role).toBe('user');
    expect(result.current.messages[0].content).toBe('Hi there');
    expect(result.current.messages[1].role).toBe('assistant');
    expect(result.current.messages[1].content).toBe('Hello!');
    expect(result.current.sessionId).toBe('session-1');
    expect(result.current.isLoading).toBe(false);
  });

  it('sets sessionId from initial options', () => {
    const { result } = renderHook(() =>
      useChat({ sessionId: 'existing-session', autoCreate: false })
    );

    expect(result.current.sessionId).toBe('existing-session');
  });

  it('sets error when send fails', async () => {
    (api.post as ReturnType<typeof vi.fn>).mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useChat({ autoCreate: false }));

    await act(async () => {
      await result.current.send('Hello');
    });

    expect(result.current.error).toBe('Network error');
    expect(result.current.messages).toHaveLength(0);
    expect(result.current.isLoading).toBe(false);
  });

  it('ignores empty messages', async () => {
    const { result } = renderHook(() => useChat({ autoCreate: false }));

    await act(async () => {
      await result.current.send('   ');
    });

    expect(api.post).not.toHaveBeenCalled();
    expect(result.current.messages).toHaveLength(0);
  });

  it('clear resets all state', async () => {
    (api.post as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      id: 'msg-1',
      role: 'assistant',
      content: 'Hi',
      session_id: 'session-1',
    });

    const { result } = renderHook(() => useChat({ autoCreate: false }));

    await act(async () => {
      await result.current.send('Hello');
    });

    expect(result.current.messages.length).toBeGreaterThan(0);

    act(() => {
      result.current.clear();
    });

    expect(result.current.messages).toEqual([]);
    expect(result.current.error).toBeNull();
    expect(result.current.sessionId).toBeNull();
  });

  it('reload fetches messages for existing session', async () => {
    const mockMessages = [
      { id: 'm1', role: 'user', content: 'Hi', timestamp: '2024-01-01T00:00:00Z' },
    ];

    (api.get as ReturnType<typeof vi.fn>).mockResolvedValueOnce({ messages: mockMessages });

    const { result } = renderHook(() =>
      useChat({ sessionId: 'session-1', autoCreate: false })
    );

    await act(async () => {
      await result.current.reload();
    });

    expect(api.get).toHaveBeenCalledWith('/sessions/session-1');
    expect(result.current.messages).toEqual(mockMessages);
  });

  it('reload does nothing without sessionId', async () => {
    const { result } = renderHook(() => useChat({ autoCreate: false }));

    await act(async () => {
      await result.current.reload();
    });

    expect(api.get).not.toHaveBeenCalled();
  });
});
