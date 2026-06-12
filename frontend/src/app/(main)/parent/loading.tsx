'use client';

export default function ParentLoading() {
  return (
    <div className="space-y-6">
      <div className="mx-auto max-w-4xl px-4 py-8">
        <div className="mb-8 h-12 w-48 animate-pulse rounded-lg bg-slate-200 dark:bg-slate-700" />
        <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-28 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-700" />
          ))}
        </div>
        <div className="mb-6 h-64 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-700" />
        <div className="h-48 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-700" />
      </div>
    </div>
  );
}