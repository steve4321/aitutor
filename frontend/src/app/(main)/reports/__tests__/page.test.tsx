import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderWithProviders, screen, waitFor } from '@/test/utils';
import type { DailyReport, WeeklyReport } from '@/types/report';

const { apiGetMock } = vi.hoisted(() => ({
  apiGetMock: vi.fn<(endpoint: string, params?: Record<string, string>) => Promise<unknown>>(),
}));

vi.mock('@/lib/api', () => ({
  api: { get: apiGetMock },
}));

import ReportsPage from '../page';

const mockDailyReport: DailyReport = {
  date: '2024-06-16',
  sessions_count: 2,
  problems_attempted: 10,
  problems_correct: 7,
  xp_earned: 150,
  time_spent_minutes: 45,
  knowledge_points_reviewed: [],
};

const mockWeeklyReport: WeeklyReport = {
  week_start: '2024-06-10',
  week_end: '2024-06-16',
  total_sessions: 8,
  total_problems: 40,
  total_correct: 28,
  total_xp: 600,
  total_time_minutes: 180,
  streak_days: 5,
  mastery_changes: {},
  subject_breakdown: {
    math: {
      total_problems: 25,
      total_correct: 18,
      total_xp: 375,
      total_time_minutes: 120,
      sessions_count: 5,
    },
    english: {
      total_problems: 15,
      total_correct: 10,
      total_xp: 225,
      total_time_minutes: 60,
      sessions_count: 3,
    },
  },
};

function setupLoadedMocks() {
  apiGetMock.mockImplementation((endpoint) => {
    if (endpoint === '/reports/daily') return Promise.resolve(mockDailyReport);
    if (endpoint === '/reports/weekly') return Promise.resolve(mockWeeklyReport);
    return Promise.resolve(null);
  });
}

function setupEmptyMocks() {
  apiGetMock.mockResolvedValue(null);
}

describe('Reports Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading skeleton initially', () => {
    apiGetMock.mockReturnValue(new Promise<unknown>(() => {}));

    const { container } = renderWithProviders(<ReportsPage />);

    const skeletons = container.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('renders reports page with header when data loads', async () => {
    setupLoadedMocks();

    renderWithProviders(<ReportsPage />);

    await waitFor(() => {
      expect(screen.getByText('学习报告')).toBeInTheDocument();
    });
    expect(screen.getByText('追踪你的学习进度和表现')).toBeInTheDocument();
  });

  it('handles no-data state when reports are null', async () => {
    setupEmptyMocks();

    renderWithProviders(<ReportsPage />);

    await waitFor(() => {
      expect(screen.getByText('暂无数据')).toBeInTheDocument();
    });
    expect(screen.getByText('开始学习后查看你的学习报告')).toBeInTheDocument();
  });

  it('handles error state', async () => {
    apiGetMock.mockRejectedValue(new Error('Network error'));

    renderWithProviders(<ReportsPage />);

    await waitFor(() => {
      expect(screen.getByText('暂无数据')).toBeInTheDocument();
    });
  });

  it('renders time range buttons when data is present', async () => {
    setupLoadedMocks();

    renderWithProviders(<ReportsPage />);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: '本周' })).toBeInTheDocument();
    });
    expect(screen.getByRole('button', { name: '本月' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '全部' })).toBeInTheDocument();
  });

  it('renders stat cards with data when loaded', async () => {
    setupLoadedMocks();

    renderWithProviders(<ReportsPage />);

    await waitFor(() => {
      expect(screen.getByText('获得 XP')).toBeInTheDocument();
    });
    expect(screen.getByText('完成题目')).toBeInTheDocument();
    expect(screen.getByText('正确率')).toBeInTheDocument();
    expect(screen.getByText('学习时间')).toBeInTheDocument();
  });

  it('renders subject breakdown section', async () => {
    setupLoadedMocks();

    renderWithProviders(<ReportsPage />);

    await waitFor(() => {
      expect(screen.getAllByText('数学').length).toBeGreaterThan(0);
    });
    expect(screen.getAllByText('英语').length).toBeGreaterThan(0);
  });
});
