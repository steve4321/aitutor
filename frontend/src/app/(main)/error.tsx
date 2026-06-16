'use client';

export default function MainError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex items-center justify-center min-h-[50vh]" role="alert">
      <div className="text-center space-y-4">
        <h2 className="text-lg font-semibold text-foreground">加载失败</h2>
        <p className="text-sm text-muted-foreground">{error.message || '请稍后重试'}</p>
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