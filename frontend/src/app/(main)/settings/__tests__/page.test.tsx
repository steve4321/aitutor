import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderWithProviders, screen, waitFor } from '@/test/utils';
import type {
  StudentProfileResponse,
  UserResponse,
  UserPreferencesResponse,
} from '@/types/user';

const { apiGetMock, apiPutMock, apiPatchMock, apiPostMock, mockRouter, mockSignOut } = vi.hoisted(() => ({
  apiGetMock: vi.fn<(endpoint: string, params?: Record<string, string>) => Promise<unknown>>(),
  apiPutMock: vi.fn<(endpoint: string, body?: unknown) => Promise<unknown>>(),
  apiPatchMock: vi.fn<(endpoint: string, body?: unknown) => Promise<unknown>>(),
  apiPostMock: vi.fn<(endpoint: string, body?: unknown) => Promise<unknown>>(),
  mockRouter: { push: vi.fn() },
  mockSignOut: vi.fn(),
}));

vi.mock('@/lib/api', () => ({
  api: {
    get: apiGetMock,
    put: apiPutMock,
    patch: apiPatchMock,
    post: apiPostMock,
  },
}));

vi.mock('next/navigation', () => ({
  useRouter: () => mockRouter,
}));

vi.mock('@/hooks/use-auth', () => ({
  useAuth: () => ({ signOut: mockSignOut }),
}));

vi.mock('next-themes', () => ({
  useTheme: () => ({ theme: 'light', setTheme: vi.fn() }),
}));

vi.mock('@/hooks/use-eink', () => ({
  useEInk: () => ({
    isEInk: false,
    preference: 'auto' as const,
    setPreference: vi.fn(),
    toggleEInkMode: vi.fn(),
    autoDetect: vi.fn(),
  }),
}));

import SettingsPage from '../page';

const mockUser: UserResponse = {
  id: 'user-1',
  email: 'test@example.com',
  phone: null,
  name: '小明',
  role: 'student',
  avatar_url: null,
  created_at: '2024-01-01T00:00:00Z',
};

const mockProfile: StudentProfileResponse = {
  id: 'profile-1',
  user_id: 'user-1',
  grade_level: 5,
  target_exam: null,
  target_date: null,
  daily_goal_minutes: 30,
  timezone: 'Asia/Shanghai',
  preferred_lang: 'zh-CN',
  diagnostic_done: false,
  xp_total: 100,
  streak_days: 3,
  longest_streak: 5,
  minutes_today: 15,
};

const mockPrefs: UserPreferencesResponse = {
  language: 'zh-CN',
  font_size: 16,
  sound_enabled: true,
  notifications_enabled: true,
  theme: 'light',
};

function setupLoadedMocks() {
  apiGetMock.mockImplementation((endpoint) => {
    if (endpoint === '/users/me/profile') return Promise.resolve(mockProfile);
    if (endpoint === '/users/me') return Promise.resolve(mockUser);
    if (endpoint === '/users/me/preferences') return Promise.resolve(mockPrefs);
    return Promise.resolve(null);
  });
}

describe('Settings Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockRouter.push.mockClear();
    mockSignOut.mockClear();
  });

  it('renders the settings page header', async () => {
    setupLoadedMocks();

    renderWithProviders(<SettingsPage />);

    await waitFor(() => {
      expect(screen.getByText('设置')).toBeInTheDocument();
    });
    expect(screen.getByText('管理你的账户和偏好设置')).toBeInTheDocument();
  });

  it('shows user profile section', async () => {
    setupLoadedMocks();

    renderWithProviders(<SettingsPage />);

    expect(screen.getByText('个人资料')).toBeInTheDocument();
  });

  it('shows loading spinner in profile when data is loading', () => {
    apiGetMock.mockReturnValue(new Promise<unknown>(() => {}));

    renderWithProviders(<SettingsPage />);

    expect(screen.getByText('设置')).toBeInTheDocument();
    expect(screen.queryByDisplayValue('小明')).not.toBeInTheDocument();
  });

  it('shows display name input after data loads', async () => {
    setupLoadedMocks();

    renderWithProviders(<SettingsPage />);

    await waitFor(() => {
      expect(screen.getByDisplayValue('小明')).toBeInTheDocument();
    });
  });

  it('renders preferences section', async () => {
    setupLoadedMocks();

    renderWithProviders(<SettingsPage />);

    await waitFor(() => {
      expect(screen.getByText('偏好设置')).toBeInTheDocument();
    });
    expect(screen.getByText('主题')).toBeInTheDocument();
    expect(screen.getByText('语言')).toBeInTheDocument();
    expect(screen.getByText('字体大小')).toBeInTheDocument();
  });

  it('renders display mode section', async () => {
    setupLoadedMocks();

    renderWithProviders(<SettingsPage />);

    await waitFor(() => {
      expect(screen.getByText('显示模式')).toBeInTheDocument();
    });
    expect(screen.getAllByText('自动检测设备').length).toBeGreaterThan(0);
    expect(screen.getByText('墨水屏模式')).toBeInTheDocument();
    expect(screen.getByText('标准模式')).toBeInTheDocument();
  });

  it('renders parent binding section', async () => {
    setupLoadedMocks();

    renderWithProviders(<SettingsPage />);

    await waitFor(() => {
      expect(screen.getByText('家长绑定')).toBeInTheDocument();
    });
    expect(screen.getByPlaceholderText('请输入6位绑定码')).toBeInTheDocument();
  });

  it('renders notifications and sound section', async () => {
    setupLoadedMocks();

    renderWithProviders(<SettingsPage />);

    await waitFor(() => {
      expect(screen.getByText('通知与声音')).toBeInTheDocument();
    });
    expect(screen.getByText('声音效果')).toBeInTheDocument();
    expect(screen.getByText('推送通知')).toBeInTheDocument();
  });

  it('renders logout button', async () => {
    setupLoadedMocks();

    renderWithProviders(<SettingsPage />);

    await waitFor(() => {
      expect(screen.getByText('退出登录')).toBeInTheDocument();
    });
  });
});
