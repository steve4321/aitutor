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
        <div className="flex flex-col items-center justify-center rounded-2xl border border-muted bg-card p-12">
          <div className="h-8 w-8 bg-muted rounded-full animate-spin" />
          <div className="h-4 w-32 bg-muted rounded mt-4" />
        </div>
      </div>
    </div>
  );
}