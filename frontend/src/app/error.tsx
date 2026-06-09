'use client';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center space-y-4">
        <h2 className="text-xl font-semibold text-foreground">出了点问题</h2>
        <p className="text-muted-foreground">{error.message || '发生了未知错误'}</p>
        <button
          onClick={reset}
          className="px-4 py-2 rounded-lg bg-[var(--color-primary)] text-white hover:opacity-90 transition-opacity"
        >
          重试
        </button>
      </div>
    </div>
  );
}