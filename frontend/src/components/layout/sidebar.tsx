'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Home,
  BookOpen,
  Target,
  BarChart3,
  Settings,
  Headphones,
  X,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

const navItems = [
  { href: '/home', icon: Home, label: '首页' },
  { href: '/courses', icon: BookOpen, label: '课程' },
  { href: '/practice', icon: Target, label: '练习' },
  { href: '/ket', icon: Headphones, label: 'KET英语' },
  { href: '/reports', icon: BarChart3, label: '学习报告' },
  { href: '/settings', icon: Settings, label: '设置' },
];

export function Sidebar({ open, onClose }: SidebarProps) {
  const pathname = usePathname();

  return (
    <>
      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/30 lg:hidden"
          onClick={onClose}
        />
      )}
      <aside
        className={cn(
          'fixed left-0 top-0 z-50 h-full w-64 transform bg-white shadow-xl transition-transform duration-300 lg:relative lg:translate-x-0 lg:shadow-none lg:border-r lg:border-gray-200',
          open ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex items-center justify-between border-b border-gray-100 px-4 py-4">
          <h2 className="text-lg font-bold text-gray-900">AI私人家教</h2>
          <button
            onClick={onClose}
            className="rounded-full p-1 text-gray-400 hover:bg-gray-100 lg:hidden"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="flex flex-col gap-1 p-3">
          {navItems.map((item) => {
            const isActive = pathname?.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onClose}
                className={cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                )}
              >
                <item.icon className="h-5 w-5" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>
    </>
  );
}
