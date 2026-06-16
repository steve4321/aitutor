'use client';

import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Link from 'next/link';
import {
  Settings,
  Bell,
  Clock,
  Link2,
  ArrowLeft,
  Loader2,
  Check,
  X,
  Plus,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';
import { ROUTES } from '@/lib/constants';
import type { LinkedChild, NotificationPreferences, LinkChildResponse } from '@/types/parent';

const WEEKDAYS = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];

export default function ParentSettingsPage() {
  const queryClient = useQueryClient();

  const [notifications, setNotifications] = useState({
    milestone_notifications: true,
    achievement_notifications: true,
    concern_alerts: true,
    weekly_reports: true,
  });
  const [weeklyReportDay, setWeeklyReportDay] = useState(1);
  const [weeklyReportTime, setWeeklyReportTime] = useState('09:00');
  const [studyTimeLimit, setStudyTimeLimit] = useState<string>('');
  const [linkCode, setLinkCode] = useState('');
  const [linkMessage, setLinkMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const { data: children, isLoading: childrenLoading } = useQuery<LinkedChild[]>({
    queryKey: ['parent-children'],
    queryFn: () => api.get<LinkedChild[]>('/parent/children'),
  });

  const { data: prefs, isLoading: prefsLoading } = useQuery<NotificationPreferences>({
    queryKey: ['parent-notification-prefs'],
    queryFn: () => api.get<NotificationPreferences>('/parent/notification-preferences'),
  });

  useEffect(() => {
    if (prefs) {
      setNotifications({
        milestone_notifications: prefs.milestone_notifications,
        achievement_notifications: prefs.achievement_notifications,
        concern_alerts: prefs.concern_alerts,
        weekly_reports: prefs.weekly_reports,
      });
      setWeeklyReportDay(prefs.weekly_report_day);
      setWeeklyReportTime(prefs.weekly_report_time);
      if (prefs.study_time_limit_minutes) {
        setStudyTimeLimit(String(prefs.study_time_limit_minutes));
      }
    }
  }, [prefs]);

  const savePrefsMutation = useMutation({
    mutationFn: (updates: Partial<NotificationPreferences>) =>
      api.patch<NotificationPreferences>('/parent/notification-preferences', updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['parent-notification-prefs'] });
    },
  });

  const linkChildMutation = useMutation({
    mutationFn: (code: string) =>
      api.post<LinkChildResponse>('/parent/children/link', { link_code: code }),
    onSuccess: (data) => {
      if (data.status === 'already_linked') {
        setLinkMessage({ type: 'success', text: `已绑定 ${data.child_name ?? '孩子'}` });
      } else {
        setLinkMessage({ type: 'success', text: `绑定成功！${data.child_name ? `已关联 ${data.child_name}` : ''}` });
      }
      setLinkCode('');
      queryClient.invalidateQueries({ queryKey: ['parent-children'] });
      setTimeout(() => setLinkMessage(null), 4000);
    },
    onError: () => {
      setLinkMessage({ type: 'error', text: '绑定失败，请检查绑定码是否正确' });
      setTimeout(() => setLinkMessage(null), 4000);
    },
  });

  const handleToggleNotification = (key: keyof typeof notifications) => {
    const newValue = !notifications[key];
    setNotifications((prev) => ({ ...prev, [key]: newValue }));
    savePrefsMutation.mutate({ [key]: newValue });
  };

  const handleWeeklyReportDayChange = (day: number) => {
    setWeeklyReportDay(day);
    savePrefsMutation.mutate({ weekly_report_day: day });
  };

  const handleWeeklyReportTimeChange = (time: string) => {
    setWeeklyReportTime(time);
    savePrefsMutation.mutate({ weekly_report_time: time });
  };

  const handleStudyTimeLimitChange = (value: string) => {
    setStudyTimeLimit(value);
    const numValue = parseInt(value, 10);
    if (!isNaN(numValue) && numValue > 0) {
      savePrefsMutation.mutate({ study_time_limit_minutes: numValue });
    } else if (value === '' || value === '0') {
      savePrefsMutation.mutate({ study_time_limit_minutes: null });
    }
  };

  const handleLinkChild = () => {
    if (linkCode.length === 6) {
      linkChildMutation.mutate(linkCode);
    }
  };

  const isLoading = childrenLoading || prefsLoading;

  return (
    <div className="space-y-6">
      <div className="mx-auto max-w-2xl px-4 py-8">
        <header className="mb-8">
          <Link
            href={ROUTES.PARENT}
            className="mb-4 inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300"
          >
            <ArrowLeft className="h-4 w-4" />
            返回
          </Link>
          <div className="flex items-center gap-3">
            <Settings className="h-8 w-8 text-slate-600 dark:text-slate-400" />
            <div>
              <h1 className="text-3xl font-bold text-slate-900 dark:text-white">设置</h1>
              <p className="text-slate-600 dark:text-slate-400">管理通知和学习限制</p>
            </div>
          </div>
        </header>

        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
          </div>
        )}

        {!isLoading && (
          <>
            <section className="mb-6 rounded-2xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800">
              <div className="border-b border-slate-200 px-6 py-4 dark:border-slate-700">
                <h2 className="flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-white">
                  <Link2 className="h-5 w-5 text-amber-600 dark:text-amber-400" />
                  关联孩子
                </h2>
              </div>
              <div className="p-6">
                {children && children.length > 0 && (
                  <div className="mb-4">
                    <p className="mb-2 text-sm font-medium text-slate-700 dark:text-slate-300">已关联的孩子</p>
                    <div className="space-y-2">
                      {children.map((child) => (
                        <div
                          key={child.id}
                          className="flex items-center justify-between rounded-lg border border-slate-100 bg-slate-50 px-4 py-3 dark:border-slate-700 dark:bg-slate-900"
                        >
                          <div className="flex items-center gap-3">
                            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-violet-500 text-sm font-bold text-white">
                              {child.name.charAt(0)}
                            </div>
                            <div>
                              <p className="font-medium text-slate-900 dark:text-white">{child.name}</p>
                              <p className="text-xs text-slate-500 dark:text-slate-400">
                                {child.grade_level ? `年级${child.grade_level}` : ''} {child.target_exam ?? ''}
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center gap-1 text-xs text-slate-500 dark:text-slate-400">
                            <span className="text-amber-500">🔥</span>
                            {child.streak_days}天连续
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                <p className="mb-4 text-sm text-slate-600 dark:text-slate-400">
                  输入孩子提供的绑定码，将他们的学习报告同步到您的账户。
                </p>
                <div className="flex gap-3">
                  <input
                    type="text"
                    value={linkCode}
                    onChange={(e) => setLinkCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    placeholder="请输入6位绑定码"
                    maxLength={6}
                    className="flex-1 rounded-lg border border-slate-200 bg-white px-4 py-3 text-center text-lg tracking-widest text-slate-900 transition-colors focus:border-blue-500 focus:outline-none dark:border-slate-700 dark:bg-slate-900 dark:text-white dark:placeholder:text-slate-500"
                  />
                  <button
                    onClick={handleLinkChild}
                    disabled={linkCode.length !== 6 || linkChildMutation.isPending}
                    className="flex items-center gap-2 rounded-lg bg-amber-600 px-6 py-3 font-medium text-white transition-all hover:bg-amber-700 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {linkChildMutation.isPending ? (
                      <Loader2 className="h-5 w-5 animate-spin" />
                    ) : (
                      <Plus className="h-5 w-5" />
                    )}
                    绑定
                  </button>
                </div>
                {linkMessage && (
                  <div
                    className={cn(
                      'mt-3 flex items-center gap-2',
                      linkMessage.type === 'success'
                        ? 'text-emerald-600 dark:text-emerald-400'
                        : 'text-rose-600 dark:text-rose-400'
                    )}
                  >
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
                  通知偏好
                </h2>
              </div>
              <div className="divide-y divide-slate-100 dark:divide-slate-700">
                <div className="flex items-center justify-between px-6 py-4">
                  <div>
                    <p className="font-medium text-slate-900 dark:text-white">知识点升级</p>
                    <p className="text-sm text-slate-500 dark:text-slate-400">孩子掌握度提升时通知</p>
                  </div>
                  <button
                    onClick={() => handleToggleNotification('milestone_notifications')}
                    className={cn(
                      'relative h-6 w-11 rounded-full transition-colors',
                      notifications.milestone_notifications ? 'bg-blue-600' : 'bg-slate-300 dark:bg-slate-600'
                    )}
                  >
                    <span
                      className={cn(
                        'absolute top-1 h-4 w-4 rounded-full bg-white shadow transition-transform',
                        notifications.milestone_notifications ? 'left-6' : 'left-1'
                      )}
                    />
                  </button>
                </div>

                <div className="flex items-center justify-between px-6 py-4">
                  <div>
                    <p className="font-medium text-slate-900 dark:text-white">成就解锁</p>
                    <p className="text-sm text-slate-500 dark:text-slate-400">获得新成就时通知</p>
                  </div>
                  <button
                    onClick={() => handleToggleNotification('achievement_notifications')}
                    className={cn(
                      'relative h-6 w-11 rounded-full transition-colors',
                      notifications.achievement_notifications ? 'bg-blue-600' : 'bg-slate-300 dark:bg-slate-600'
                    )}
                  >
                    <span
                      className={cn(
                        'absolute top-1 h-4 w-4 rounded-full bg-white shadow transition-transform',
                        notifications.achievement_notifications ? 'left-6' : 'left-1'
                      )}
                    />
                  </button>
                </div>

                <div className="flex items-center justify-between px-6 py-4">
                  <div>
                    <p className="font-medium text-slate-900 dark:text-white">异常提醒</p>
                    <p className="text-sm text-slate-500 dark:text-slate-400">知识点退步或学习异常时通知</p>
                  </div>
                  <button
                    onClick={() => handleToggleNotification('concern_alerts')}
                    className={cn(
                      'relative h-6 w-11 rounded-full transition-colors',
                      notifications.concern_alerts ? 'bg-blue-600' : 'bg-slate-300 dark:bg-slate-600'
                    )}
                  >
                    <span
                      className={cn(
                        'absolute top-1 h-4 w-4 rounded-full bg-white shadow transition-transform',
                        notifications.concern_alerts ? 'left-6' : 'left-1'
                      )}
                    />
                  </button>
                </div>

                <div className="flex items-center justify-between px-6 py-4">
                  <div>
                    <p className="font-medium text-slate-900 dark:text-white">周报推送</p>
                    <p className="text-sm text-slate-500 dark:text-slate-400">每周发送学习报告摘要</p>
                  </div>
                  <button
                    onClick={() => handleToggleNotification('weekly_reports')}
                    className={cn(
                      'relative h-6 w-11 rounded-full transition-colors',
                      notifications.weekly_reports ? 'bg-blue-600' : 'bg-slate-300 dark:bg-slate-600'
                    )}
                  >
                    <span
                      className={cn(
                        'absolute top-1 h-4 w-4 rounded-full bg-white shadow transition-transform',
                        notifications.weekly_reports ? 'left-6' : 'left-1'
                      )}
                    />
                  </button>
                </div>
              </div>
            </section>

            <section className="mb-6 rounded-2xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800">
              <div className="border-b border-slate-200 px-6 py-4 dark:border-slate-700">
                <h2 className="flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-white">
                  <Clock className="h-5 w-5 text-violet-600 dark:text-violet-400" />
                  周报推送时间
                </h2>
              </div>
              <div className="p-6">
                <div className="flex flex-wrap gap-3">
                  {WEEKDAYS.map((day, index) => (
                    <button
                      key={day}
                      onClick={() => handleWeeklyReportDayChange(index)}
                      className={cn(
                        'rounded-lg px-4 py-2 text-sm transition-all',
                        weeklyReportDay === index
                          ? 'bg-violet-600 text-white'
                          : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600'
                      )}
                    >
                      {day}
                    </button>
                  ))}
                </div>
                <div className="mt-4">
                  <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">
                    推送时间
                  </label>
                  <input
                    type="time"
                    value={weeklyReportTime}
                    onChange={(e) => handleWeeklyReportTimeChange(e.target.value)}
                    className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-slate-900 transition-colors focus:border-blue-500 focus:outline-none dark:border-slate-700 dark:bg-slate-900 dark:text-white"
                  />
                </div>
              </div>
            </section>

            <section className="mb-6 rounded-2xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800">
              <div className="border-b border-slate-200 px-6 py-4 dark:border-slate-700">
                <h2 className="flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-white">
                  <Clock className="h-5 w-5 text-amber-600 dark:text-amber-400" />
                  每日学习时长限制
                </h2>
              </div>
              <div className="p-6">
                <p className="mb-4 text-sm text-slate-600 dark:text-slate-400">
                  设置孩子每天的最大学习时长，超出后系统将提醒休息。（留空表示不限制）
                </p>
                <div className="flex items-center gap-3">
                  <input
                    type="number"
                    value={studyTimeLimit}
                    onChange={(e) => handleStudyTimeLimitChange(e.target.value)}
                    placeholder="不限制"
                    min="0"
                    max="480"
                    className="w-32 rounded-lg border border-slate-200 bg-white px-4 py-2 text-slate-900 transition-colors focus:border-blue-500 focus:outline-none dark:border-slate-700 dark:bg-slate-900 dark:text-white"
                  />
                  <span className="text-sm text-slate-500 dark:text-slate-400">分钟/天</span>
                </div>
              </div>
            </section>
          </>
        )}
      </div>
    </div>
  );
}