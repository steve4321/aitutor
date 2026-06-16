'use client';

import { Flame, Bell, Settings } from 'lucide-react';
import Link from 'next/link';
import { Avatar } from '@/components/ui/avatar';

interface HeaderProps {
  streak?: number;
  xp?: number;
  userName?: string;
  avatarUrl?: string;
}

export function Header({
  streak = 7,
  xp = 1250,
  userName = '同学',
  avatarUrl,
}: HeaderProps) {
  return (
    <header className="sticky top-0 z-40 border-b border-gray-100 bg-white/95 backdrop-blur-sm">
      <div className="mx-auto flex max-w-lg items-center justify-between px-4 py-3">
        <div className="flex items-center gap-3">
          <Avatar src={avatarUrl} alt={userName} size="sm" />
          <div>
            <p className="text-sm font-semibold text-gray-900">{userName}</p>
            <div className="flex items-center gap-3 text-xs text-gray-500">
              <span className="flex items-center gap-1">
                <Flame className="h-3.5 w-3.5 text-orange-500" />
                {streak}天连续
              </span>
              <span className="text-yellow-600 font-medium">{xp} XP</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button className="relative rounded-full p-2 text-gray-500 hover:bg-gray-100" aria-label="通知">
            <Bell className="h-5 w-5" />
            <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-red-500" />
          </button>
          <Link
            href="/settings"
            className="rounded-full p-2 text-gray-500 hover:bg-gray-100"
          >
            <Settings className="h-5 w-5" />
          </Link>
        </div>
      </div>
    </header>
  );
}
