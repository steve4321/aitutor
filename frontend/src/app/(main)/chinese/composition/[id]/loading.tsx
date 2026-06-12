export default function Loading() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="mx-auto max-w-3xl px-4 py-8">
        <div className="flex items-center gap-4 mb-6">
          <div className="h-10 w-10 bg-muted rounded-full" />
          <div className="space-y-2">
            <div className="h-6 w-24 bg-muted rounded" />
            <div className="h-4 w-32 bg-muted rounded" />
          </div>
        </div>
        <div className="rounded-xl bg-amber-50 border border-amber-200 px-4 py-3 h-20" />
        <div className="mt-6 rounded-xl border border-muted bg-card p-4">
          <div className="min-h-[400px] bg-muted rounded-xl" />
        </div>
        <div className="mt-4 flex justify-between items-center">
          <div className="h-4 w-32 bg-muted rounded" />
          <div className="h-10 w-28 bg-muted rounded-xl" />
        </div>
      </div>
    </div>
  );
}