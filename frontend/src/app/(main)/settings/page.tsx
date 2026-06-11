'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useTheme } from 'next-themes';
import {
  Settings,
  User,
  Palette,
  Bell,
  Volume2,
  Link,
  LogOut,
  Check,
  X,
  Moon,
  Sun,
  Loader2,
  Pencil,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuth } from '@/hooks/use-auth';
import { api } from '@/lib/api';
import { ROUTES } from '@/lib/constants';
import type { StudentProfileResponse, UserResponse } from '@/types/user';

type Theme = 'light' | 'dark' | 'system';
type Language = 'zh-CN' | 'en';
type FontSize = 'small' | 'medium' | 'large';

export default function SettingsPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { signOut } = useAuth();
  const { theme: activeTheme, setTheme: setActiveTheme } = useTheme();

  const [displayName, setDisplayName] = useState('');
  const [gradeLevel, setGradeLevel] = useState(6);
  const [language, setLanguage] = useState<Language>('zh-CN');
  const [fontSize, setFontSize] = useState<FontSize>('medium');
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [parentLinkCode, setParentLinkCode] = useState('');
  const [linkMessage, setLinkMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [avatarUrl] = useState<string | null>(null);

  const profileQuery = useQuery({
    queryKey: ['profile'],
    queryFn: () => api.get<StudentProfileResponse>('/users/me/profile'),
  });

  const userQuery = useQuery({
    queryKey: ['me'],
    queryFn: () => api.get<UserResponse>('/users/me'),
  });

  useEffect(() => {
    if (userQuery.data) {
      setDisplayName(userQuery.data.name);
    }
  }, [userQuery.data]);

  useEffect(() => {
    if (profileQuery.data?.grade_level != null) {
      setGradeLevel(profileQuery.data.grade_level);
    }
  }, [profileQuery.data]);

  const saveNameMutation = useMutation({
    mutationFn: (name: string) =>
      api.put<UserResponse>('/users/me', { name }),
    onSuccess: (data) => {
      queryClient.setQueryData(['me'], data);
    },
  });

  const saveProfileMutation = useMutation({
    mutationFn: (updates: { grade_level?: number; target_exam?: string }) =>
      api.patch<StudentProfileResponse>('/users/me/profile', updates),
    onSuccess: (data) => {
      queryClient.setQueryData(['profile'], data);
    },
  });

  const parentLinkMutation = useMutation({
    mutationFn: (code: string) =>
      api.post<{ status: string; parent_name?: string }>('/parent/link', { link_code: code }),
    onSuccess: (data) => {
      if (data.status === 'already_linked') {
        setLinkMessage({ type: 'success', text: `已绑定 ${data.parent_name ?? '家长'}` });
      } else {
        setLinkMessage({ type: 'success', text: `绑定成功！${data.parent_name ? `已关联 ${data.parent_name}` : ''}` });
      }
      setParentLinkCode('');
      setTimeout(() => setLinkMessage(null), 4000);
    },
    onError: () => {
      setLinkMessage({ type: 'error', text: '绑定失败，请检查绑定码是否正确' });
      setTimeout(() => setLinkMessage(null), 4000);
    },
  });

  const handleSaveName = () => {
    const trimmed = displayName.trim();
    if (trimmed && trimmed !== (userQuery.data?.name ?? '')) {
      saveNameMutation.mutate(trimmed);
    }
  };

  const handleGradeChange = (grade: number) => {
    setGradeLevel(grade);
    saveProfileMutation.mutate({ grade_level: grade });
  };

  const handleThemeChange = (t: Theme) => {
    setActiveTheme(t);
  };

  const handleParentLink = () => {
    if (parentLinkCode.length === 6) {
      parentLinkMutation.mutate(parentLinkCode);
    }
  };

  const handleLogout = () => {
    signOut();
    router.push(ROUTES.LOGIN);
  };

  const isSaving = saveNameMutation.isPending || saveProfileMutation.isPending;
  const currentTheme = (activeTheme ?? 'system') as Theme;

  return (
    <div className="space-y-6">
      <div className="mx-auto max-w-2xl px-4 py-8">
        <header className="mb-8">
          <div className="flex items-center gap-3">
            <Settings className="h-8 w-8 text-slate-600 dark:text-slate-400" />
            <div>
              <h1 className="text-3xl font-bold text-slate-900 dark:text-white">设置</h1>
              <p className="text-slate-600 dark:text-slate-400">管理你的账户和偏好设置</p>
            </div>
          </div>
        </header>

        <section className="mb-6 rounded-2xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800">
          <div className="border-b border-slate-200 px-6 py-4 dark:border-slate-700">
            <h2 className="flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-white">
              <User className="h-5 w-5 text-blue-600 dark:text-blue-400" />
              个人资料
            </h2>
          </div>
          <div className="p-6">
            {(userQuery.isLoading || profileQuery.isLoading) && (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
              </div>
            )}
            {!userQuery.isLoading && !profileQuery.isLoading && (
              <div className="mb-6 flex items-center gap-6">
                <div className="relative">
                  <div className="flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-violet-500 text-xl font-bold text-white">
                    {avatarUrl ? (
                      <img src={avatarUrl} alt="Avatar" className="h-full w-full rounded-full object-cover" />
                    ) : (
                      displayName.charAt(0) || '?'
                    )}
                  </div>
                  <button className="absolute -bottom-1 -right-1 flex h-7 w-7 items-center justify-center rounded-full bg-slate-100 shadow-sm hover:bg-slate-200 dark:bg-slate-700 dark:hover:bg-slate-600">
                    <Pencil className="h-3.5 w-3.5" />
                  </button>
                </div>
                <div className="flex-1">
                  <div className="mb-3">
                    <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">
                      显示名称
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={displayName}
                        onChange={(e) => setDisplayName(e.target.value)}
                        onBlur={handleSaveName}
                        onKeyDown={(e) => { if (e.key === 'Enter') handleSaveName(); }}
                        className="w-full rounded-lg border border-slate-200 bg-white px-4 py-2 text-slate-900 transition-colors focus:border-blue-500 focus:outline-none dark:border-slate-700 dark:bg-slate-900 dark:text-white"
                      />
                      {saveNameMutation.isPending && (
                        <Loader2 className="h-5 w-5 animate-spin text-blue-500 self-center" />
                      )}
                      {saveNameMutation.isSuccess && (
                        <Check className="h-5 w-5 text-emerald-500 self-center" />
                      )}
                    </div>
                  </div>
                  <div>
                    <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">
                      年级
                    </label>
                    <select
                      value={gradeLevel}
                      onChange={(e) => handleGradeChange(Number(e.target.value))}
                      disabled={saveProfileMutation.isPending}
                      className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-slate-900 transition-colors focus:border-blue-500 focus:outline-none disabled:opacity-50 dark:border-slate-700 dark:bg-slate-900 dark:text-white"
                    >
                      {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((g) => (
                        <option key={g} value={g}>
                          小学{g <= 6 ? `${g}年级` : ''} {g > 6 ? `初中${g - 6}年级` : ''}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            )}
          </div>
        </section>

        <section className="mb-6 rounded-2xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800">
          <div className="border-b border-slate-200 px-6 py-4 dark:border-slate-700">
            <h2 className="flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-white">
              <Palette className="h-5 w-5 text-violet-600 dark:text-violet-400" />
              偏好设置
            </h2>
          </div>
          <div className="divide-y divide-slate-100 dark:divide-slate-700">
            <div className="flex items-center justify-between px-6 py-4">
              <div>
                <p className="font-medium text-slate-900 dark:text-white">主题</p>
                <p className="text-sm text-slate-500 dark:text-slate-400">选择应用外观</p>
              </div>
              <div className="flex gap-2">
                {([
                  { value: 'light' as Theme, icon: Sun, label: '浅色' },
                  { value: 'dark' as Theme, icon: Moon, label: '深色' },
                  { value: 'system' as Theme, icon: Settings, label: '自动' },
                ]).map((t) => (
                  <button
                    key={t.value}
                    onClick={() => handleThemeChange(t.value)}
                    className={cn(
                      'flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition-all',
                      currentTheme === t.value
                        ? 'bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-300'
                        : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'
                    )}
                  >
                    <t.icon className="h-4 w-4" />
                    {t.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex items-center justify-between px-6 py-4">
              <div>
                <p className="font-medium text-slate-900 dark:text-white">语言</p>
                <p className="text-sm text-slate-500 dark:text-slate-400">选择显示语言</p>
              </div>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value as Language)}
                className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 transition-colors focus:border-blue-500 focus:outline-none dark:border-slate-700 dark:bg-slate-900 dark:text-white"
              >
                <option value="zh-CN">简体中文</option>
                <option value="en">English</option>
              </select>
            </div>

            <div className="flex items-center justify-between px-6 py-4">
              <div>
                <p className="font-medium text-slate-900 dark:text-white">字体大小</p>
                <p className="text-sm text-slate-500 dark:text-slate-400">调整文字大小</p>
              </div>
              <div className="flex gap-2">
                {(['small', 'medium', 'large'] as FontSize[]).map((size) => (
                  <button
                    key={size}
                    onClick={() => setFontSize(size)}
                    className={cn(
                      'rounded-lg px-3 py-2 text-sm transition-all',
                      fontSize === size
                        ? 'bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-300'
                        : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'
                    )}
                  >
                    {size === 'small' && '小'}
                    {size === 'medium' && '中'}
                    {size === 'large' && '大'}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="mb-6 rounded-2xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800">
          <div className="border-b border-slate-200 px-6 py-4 dark:border-slate-700">
            <h2 className="flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-white">
              <Link className="h-5 w-5 text-amber-600 dark:text-amber-400" />
              家长绑定
            </h2>
          </div>
          <div className="p-6">
            <p className="mb-4 text-sm text-slate-600 dark:text-slate-400">
              输入家长提供的绑定码，将你的学习报告同步给家长查看。
            </p>
            <div className="flex gap-3">
              <input
                type="text"
                value={parentLinkCode}
                onChange={(e) => setParentLinkCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="请输入6位绑定码"
                maxLength={6}
                className="flex-1 rounded-lg border border-slate-200 bg-white px-4 py-3 text-center text-lg tracking-widest text-slate-900 transition-colors focus:border-blue-500 focus:outline-none dark:border-slate-700 dark:bg-slate-900 dark:text-white dark:placeholder:text-slate-500"
              />
              <button
                onClick={handleParentLink}
                disabled={parentLinkCode.length !== 6 || parentLinkMutation.isPending}
                className="rounded-lg bg-amber-600 px-6 py-3 font-medium text-white transition-all hover:bg-amber-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {parentLinkMutation.isPending ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  '绑定'
                )}
              </button>
            </div>
            {linkMessage && (
              <div className={cn(
                'mt-3 flex items-center gap-2',
                linkMessage.type === 'success' ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'
              )}>
                {linkMessage.type === 'success' ? (
                  <Check className="h-5 w-5" />
                ) : (
                  <X className="h-5 w-5" />
                )}
                <span>{linkMessage.text}</span>
              </div>
            )}
          </div>
        </section>

        <section className="mb-6 rounded-2xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800">
          <div className="border-b border-slate-200 px-6 py-4 dark:border-slate-700">
            <h2 className="flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-white">
              <Bell className="h-5 w-5 text-rose-600 dark:text-rose-400" />
              通知与声音
            </h2>
          </div>
          <div className="divide-y divide-slate-100 dark:divide-slate-700">
            <div className="flex items-center justify-between px-6 py-4">
              <div className="flex items-center gap-3">
                <Volume2 className="h-5 w-5 text-slate-400" />
                <div>
                  <p className="font-medium text-slate-900 dark:text-white">声音效果</p>
                  <p className="text-sm text-slate-500 dark:text-slate-400">操作反馈音效</p>
                </div>
              </div>
              <button
                onClick={() => setSoundEnabled(!soundEnabled)}
                className={cn(
                  'relative h-6 w-11 rounded-full transition-colors',
                  soundEnabled ? 'bg-blue-600' : 'bg-slate-300 dark:bg-slate-600'
                )}
              >
                <span
                  className={cn(
                    'absolute top-1 h-4 w-4 rounded-full bg-white shadow transition-transform',
                    soundEnabled ? 'left-6' : 'left-1'
                  )}
                />
              </button>
            </div>

            <div className="flex items-center justify-between px-6 py-4">
              <div className="flex items-center gap-3">
                <Bell className="h-5 w-5 text-slate-400" />
                <div>
                  <p className="font-medium text-slate-900 dark:text-white">推送通知</p>
                  <p className="text-sm text-slate-500 dark:text-slate-400">学习提醒和成绩通知</p>
                </div>
              </div>
              <button
                onClick={() => setNotificationsEnabled(!notificationsEnabled)}
                className={cn(
                  'relative h-6 w-11 rounded-full transition-colors',
                  notificationsEnabled ? 'bg-blue-600' : 'bg-slate-300 dark:bg-slate-600'
                )}
              >
                <span
                  className={cn(
                    'absolute top-1 h-4 w-4 rounded-full bg-white shadow transition-transform',
                    notificationsEnabled ? 'left-6' : 'left-1'
                  )}
                />
              </button>
            </div>
          </div>
        </section>

        <button
          onClick={handleLogout}
          className="flex w-full items-center justify-center gap-2 rounded-xl border border-rose-200 py-4 font-medium text-rose-600 transition-all hover:bg-rose-50 dark:border-rose-800 dark:text-rose-400 dark:hover:bg-rose-900/20"
        >
          <LogOut className="h-5 w-5" />
          退出登录
        </button>
      </div>
    </div>
  );
}
