'use client';

export default function ParentSettingsLoading() {
  return (
    <div className="space-y-6">
      <div className="mx-auto max-w-2xl px-4 py-8">
        <div className="mb-8 h-12 w-48 animate-pulse rounded-lg bg-slate-200 dark:bg-slate-700" />
        <div className="mb-6 space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-32 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-700" />
          ))}
        </div>
      </div>
    </div>
  );
}