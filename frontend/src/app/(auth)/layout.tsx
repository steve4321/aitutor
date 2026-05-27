import type { ReactNode } from 'react';

export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[var(--color-primary)]/10 via-background to-[var(--color-secondary)]/10 px-4">
      <div className="w-full max-w-md">
        <div className="flex justify-center mb-8">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-[var(--color-primary)] flex items-center justify-center">
              <svg
                className="w-6 h-6 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 6.253v13m0-13c-2.5-1-4-2.5-4-5.5c0-3.5 2.5-6 6-6c3.5 0 6 2.5 6 6c0 3-1.5 4.5-4 5.5z"
                />
              </svg>
            </div>
            <span className="text-2xl font-bold text-foreground">AI Tutor</span>
          </div>
        </div>

        <div className="bg-background rounded-2xl border border-border shadow-lg p-6 sm:p-8">
          {children}
        </div>
      </div>
    </div>
  );
}