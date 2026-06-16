import { cn } from '@/lib/utils';

interface LoadingSkeletonProps {
  className?: string;
}

export function LoadingSkeleton({ className = '' }: LoadingSkeletonProps) {
  return (
    <div
      className={cn(
        'animate-pulse rounded bg-[var(--color-muted)]',
        className
      )}
      aria-hidden="true"
    />
  );
}

export function MathSkeleton({ displayMode = false }: { displayMode?: boolean }) {
  if (displayMode) {
    return (
      <div className="flex items-center justify-center p-4">
        <LoadingSkeleton className="h-12 w-48" />
      </div>
    );
  }
  return <LoadingSkeleton className="h-6 w-24" />;
}

export function AnimationSkeleton() {
  return (
    <div className="aspect-video bg-[var(--color-surface-muted)] rounded-xl flex items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-[var(--color-border)] border-t-[var(--color-primary)]" />
    </div>
  );
}