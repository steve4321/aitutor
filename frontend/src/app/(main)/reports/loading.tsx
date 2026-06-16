export default function Loading() {
  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <div className="mb-8 h-12 w-48 animate-pulse rounded-lg bg-slate-200 dark:bg-slate-700" />
      <div className="mb-6 flex gap-2">
        <div className="h-10 w-16 animate-pulse rounded-lg bg-slate-200 dark:bg-slate-700" />
        <div className="h-10 w-16 animate-pulse rounded-lg bg-slate-200 dark:bg-slate-700" />
        <div className="h-10 w-16 animate-pulse rounded-lg bg-slate-200 dark:bg-slate-700" />
      </div>
      <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-28 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-700" />
        ))}
      </div>
      <div className="h-64 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-700" />
    </div>
  );
}