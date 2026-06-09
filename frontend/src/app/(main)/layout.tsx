'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { Home, BookOpen, Target, Settings as SettingsIcon } from 'lucide-react';
import { isAuthenticated } from '@/lib/auth';
import { ROUTES } from '@/lib/constants';
import { cn } from '@/lib/utils';
import { ErrorBoundary } from '@/components/error-boundary';

const NAV_ITEMS = [
  { href: '/home', label: 'Home', Icon: Home },
  { href: '/courses', label: 'Courses', Icon: BookOpen },
  { href: '/practice', label: 'Practice', Icon: Target },
  { href: '/settings', label: 'Settings', Icon: SettingsIcon },
] as const;

export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (!isAuthenticated()) {
      router.push(ROUTES.LOGIN);
    }
  }, [router]);

  if (!mounted) {
    return null;
  }

  if (!isAuthenticated()) {
    return null;
  }

  return (
    <div className="h-dvh bg-background flex flex-col overflow-hidden">
      <header className="shrink-0 z-40 bg-background/95 backdrop-blur border-b border-border">
        <div className="flex items-center justify-between px-4 h-14">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-[var(--color-primary)] flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-foreground">AI Tutor</span>
          </div>
          <Link
            href={ROUTES.SETTINGS}
            className="p-2 rounded-lg hover:bg-accent transition-colors"
            aria-label="Settings"
          >
            <SettingsIcon className="w-5 h-5 text-foreground" />
          </Link>
        </div>
      </header>

      <main className="flex-1 min-h-0 overflow-y-auto px-4 py-6">
        <ErrorBoundary>
          {children}
        </ErrorBoundary>
      </main>

      <nav className="shrink-0 bg-background border-t border-border z-50">
        <div className="flex items-center justify-around h-16 max-w-lg mx-auto">
          {NAV_ITEMS.map((item) => {
            const active = pathname === item.href || pathname.startsWith(item.href + '/');
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'flex flex-col items-center gap-1 transition-colors',
                  active
                    ? 'text-[var(--color-primary)]'
                    : 'text-muted-foreground hover:text-foreground'
                )}
              >
                <item.Icon className="w-5 h-5" />
                <span className={cn('text-xs', active && 'font-medium')}>
                  {item.label}
                </span>
              </Link>
            );
          })}
        </div>
      </nav>
    </div>
  );
}