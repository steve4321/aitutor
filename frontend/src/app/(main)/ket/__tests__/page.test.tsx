import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderWithProviders, screen, waitFor } from '@/test/utils';
import type { KETQuestionListResponse, KETWritingTask, KETSpeakingTask } from '@/types/ket';

const { apiGetMock } = vi.hoisted(() => ({
  apiGetMock: vi.fn<(endpoint: string, params?: Record<string, string>) => Promise<unknown>>(),
}));

vi.mock('@/lib/api', () => ({
  api: { get: apiGetMock },
}));

import KETPage from '../page';

const mockReadingData: KETQuestionListResponse = {
  items: [],
  total: 10,
  limit: 1,
  offset: 0,
};

const mockListeningData: KETQuestionListResponse = {
  items: [],
  total: 8,
  limit: 1,
  offset: 0,
};

const mockWritingTasks: KETWritingTask[] = [
  {
    id: 'w1',
    task_type: 'short_message',
    prompt: 'Write a short message to your friend',
    image_url: null,
    word_limit_min: 25,
    word_limit_max: 35,
    sample_response: null,
  },
];

const mockSpeakingTasks: KETSpeakingTask[] = [
  {
    id: 's1',
    topic: 'Family',
    question: 'Tell me about your family',
    difficulty: 'easy',
    expected_duration_sec: 60,
  },
];

function setupLoadedMocks() {
  apiGetMock.mockImplementation((endpoint, params) => {
    if (endpoint === '/ket/questions' && params?.skill === 'reading') {
      return Promise.resolve(mockReadingData);
    }
    if (endpoint === '/ket/questions' && params?.skill === 'listening') {
      return Promise.resolve(mockListeningData);
    }
    if (endpoint === '/ket/writing/tasks') {
      return Promise.resolve(mockWritingTasks);
    }
    if (endpoint === '/ket/speaking/tasks') {
      return Promise.resolve(mockSpeakingTasks);
    }
    return Promise.resolve([]);
  });
}

function setupEmptyMocks() {
  apiGetMock.mockImplementation((endpoint) => {
    if (endpoint === '/ket/questions') {
      return Promise.resolve({ items: [], total: 0, limit: 1, offset: 0 } satisfies KETQuestionListResponse);
    }
    if (endpoint === '/ket/writing/tasks') {
      return Promise.resolve([] satisfies KETWritingTask[]);
    }
    if (endpoint === '/ket/speaking/tasks') {
      return Promise.resolve([] satisfies KETSpeakingTask[]);
    }
    return Promise.resolve([]);
  });
}

describe('KET Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the KET hub page header', async () => {
    setupLoadedMocks();

    renderWithProviders(<KETPage />);

    await waitFor(() => {
      expect(screen.getByText('KET 英语')).toBeInTheDocument();
    });
    expect(screen.getByText('Cambridge A2 Key 备考训练')).toBeInTheDocument();
  });

  it('renders all 4 skill cards with correct titles', async () => {
    setupLoadedMocks();

    renderWithProviders(<KETPage />);

    await waitFor(() => {
      expect(screen.getByText('阅读')).toBeInTheDocument();
    });
    expect(screen.getByText('写作')).toBeInTheDocument();
    expect(screen.getByText('听力')).toBeInTheDocument();
    expect(screen.getByText('口语')).toBeInTheDocument();
  });

  it('shows loading state when data is loading', () => {
    apiGetMock.mockReturnValue(new Promise<unknown>(() => {}));

    renderWithProviders(<KETPage />);

    const loadingTexts = screen.getAllByText('加载中...');
    expect(loadingTexts).toHaveLength(4);
  });

  it('renders skill titles even during loading', () => {
    apiGetMock.mockReturnValue(new Promise<unknown>(() => {}));

    renderWithProviders(<KETPage />);

    expect(screen.getByText('阅读')).toBeInTheDocument();
    expect(screen.getByText('写作')).toBeInTheDocument();
    expect(screen.getByText('听力')).toBeInTheDocument();
    expect(screen.getByText('口语')).toBeInTheDocument();
  });

  it('shows question counts after data loads', async () => {
    setupLoadedMocks();

    renderWithProviders(<KETPage />);

    await waitFor(() => {
      expect(screen.getByText('10 个任务可用')).toBeInTheDocument();
    });
    expect(screen.getByText('8 个任务可用')).toBeInTheDocument();
    expect(screen.getAllByText('1 个任务可用')).toHaveLength(2);
  });

  it('shows em-dash for skills with no content', async () => {
    setupEmptyMocks();

    renderWithProviders(<KETPage />);

    await waitFor(() => {
      expect(screen.getAllByText('暂无内容')).toHaveLength(4);
    });
  });

  it('renders progress and recent practice sections', async () => {
    setupLoadedMocks();

    renderWithProviders(<KETPage />);

    await waitFor(() => {
      expect(screen.getByText('综合进度')).toBeInTheDocument();
    });
    expect(screen.getByText('最近练习记录')).toBeInTheDocument();
  });

  it('calls the KET question API for each skill', async () => {
    setupLoadedMocks();

    renderWithProviders(<KETPage />);

    await waitFor(() => {
      expect(apiGetMock).toHaveBeenCalledWith('/ket/questions', { skill: 'reading', limit: '1' });
    });
    expect(apiGetMock).toHaveBeenCalledWith('/ket/questions', { skill: 'listening', limit: '1' });
    expect(apiGetMock).toHaveBeenCalledWith('/ket/writing/tasks', { limit: '1' });
    expect(apiGetMock).toHaveBeenCalledWith('/ket/speaking/tasks', { limit: '1' });
  });
});
