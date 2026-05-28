'use client';

import { Home, BookOpen, Target, User } from 'lucide-react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { cn } from '@/lib/utils';

const tabs = [
  { href: '/home', icon: Home, label: '首页' },
  { href: '/courses', icon: BookOpen, label: '课程' },
  { href: '/practice', icon: Target, label: '练习' },
  { href: '/settings', icon: User, label: '我的' },
];

export function BottomNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t border-gray-200 bg-white">
      <div className="mx-auto flex max-w-lg items-center justify-around py-2">
        {tabs.map((tab) => {
          const isActive = pathname?.startsWith(tab.href);
          return (
            <Link
              key={tab.href}
              href={tab.href}
              className={cn(
                'flex flex-col items-center gap-1 px-3 py-1 text-xs transition-colors',
                isActive ? 'text-blue-600' : 'text-gray-500 hover:text-gray-700'
              )}
            >
              <tab.icon className={cn('h-5 w-5', isActive && 'fill-blue-600/20')} />
              <span className="font-medium">{tab.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
