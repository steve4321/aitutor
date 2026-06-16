import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderWithProviders, screen, waitFor } from '@/test/utils';
import type { Course, Unit, Lesson } from '@/types/course';

const { apiGetMock, apiPostMock, mockRouter } = vi.hoisted(() => ({
  apiGetMock: vi.fn<(endpoint: string, params?: Record<string, string>) => Promise<unknown>>(),
  apiPostMock: vi.fn<(endpoint: string, body?: unknown) => Promise<unknown>>(),
  mockRouter: { push: vi.fn() },
}));

vi.mock('@/lib/api', () => ({
  api: { get: apiGetMock, post: apiPostMock },
}));

vi.mock('next/navigation', () => ({
  useRouter: () => mockRouter,
}));

import PracticePage from '../page';

const mockCourses: Course[] = [
  {
    id: 'c1',
    code: 'MATH5',
    subject: 'math',
    name: '五年级数学',
    description: null,
    target_exam: null,
    estimated_hours: 40,
    is_published: true,
  },
];

const mockUnits: Unit[] = [
  {
    id: 'u1',
    course_id: 'c1',
    code: null,
    name: '第一单元',
    description: null,
    sort_order: 1,
    required_mastery: 0,
  },
];

const mockLessons: Lesson[] = [
  {
    id: 'l1',
    unit_id: 'u1',
    knowledge_point_id: null,
    code: null,
    title: '小数加减法',
    lesson_type: 'lesson',
    estimated_minutes: 20,
    sort_order: 1,
    is_published: true,
    content: null,
  },
];

function setupLoadedMocks() {
  apiGetMock.mockImplementation((endpoint) => {
    if (endpoint === '/courses') return Promise.resolve(mockCourses);
    if (endpoint.startsWith('/courses/') && endpoint.endsWith('/units')) return Promise.resolve(mockUnits);
    if (endpoint.startsWith('/courses/') && endpoint.endsWith('/lessons')) return Promise.resolve(mockLessons);
    return Promise.resolve([]);
  });
}

describe('Practice Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockRouter.push.mockClear();
  });

  it('renders the practice page with header', async () => {
    setupLoadedMocks();

    renderWithProviders(<PracticePage />);

    await waitFor(() => {
      expect(screen.getByText('选择课程和单元，开始针对性练习')).toBeInTheDocument();
    });
    expect(screen.getByText('练习')).toBeInTheDocument();
  });

  it('shows loading skeleton when courses are loading', () => {
    apiGetMock.mockReturnValue(new Promise<unknown>(() => {}));

    renderWithProviders(<PracticePage />);

    const heading = screen.getByText('练习');
    expect(heading).toBeInTheDocument();
    const skeleton = heading.parentElement?.querySelector('.animate-pulse');
    expect(skeleton).toBeTruthy();
  });

  it('renders course selection after data loads', async () => {
    setupLoadedMocks();

    renderWithProviders(<PracticePage />);

    await waitFor(() => {
      expect(screen.getByText('选择课程')).toBeInTheDocument();
    });
    expect(screen.getByText('五年级数学')).toBeInTheDocument();
  });

  it('renders unit selection after data loads', async () => {
    setupLoadedMocks();

    renderWithProviders(<PracticePage />);

    await waitFor(() => {
      expect(screen.getByText('第一单元')).toBeInTheDocument();
    });
    expect(screen.getByText('选择单元')).toBeInTheDocument();
  });

  it('shows empty state when course has no units', async () => {
    apiGetMock.mockImplementation((endpoint) => {
      if (endpoint === '/courses') return Promise.resolve(mockCourses);
      if (endpoint.startsWith('/courses/') && endpoint.endsWith('/units')) return Promise.resolve([] satisfies Unit[]);
      if (endpoint.startsWith('/courses/') && endpoint.endsWith('/lessons')) return Promise.resolve([] satisfies Lesson[]);
      return Promise.resolve([]);
    });

    renderWithProviders(<PracticePage />);

    await waitFor(() => {
      expect(screen.getByText('该课程暂无单元')).toBeInTheDocument();
    });
  });

  it('shows start practice button', async () => {
    setupLoadedMocks();

    renderWithProviders(<PracticePage />);

    await waitFor(() => {
      expect(screen.getByText('开始练习')).toBeInTheDocument();
    });
  });

  it('starts practice disabled when no units selected', async () => {
    setupLoadedMocks();

    renderWithProviders(<PracticePage />);

    await waitFor(() => {
      expect(screen.getByText('开始练习')).toBeInTheDocument();
    });
    const startButton = screen.getByText('开始练习').closest('button');
    expect(startButton).toBeDisabled();
  });
});
