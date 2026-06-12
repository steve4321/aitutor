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
        <div className="rounded-2xl border border-muted bg-card p-4 mb-4">
          <div className="flex gap-2 mb-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-8 w-16 bg-muted rounded-lg" />
            ))}
          </div>
        </div>
        <div className="rounded-2xl border border-muted bg-card p-6">
          <div className="space-y-2 text-center">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-6 w-48 bg-muted rounded mx-auto" />
            ))}
          </div>
        </div>
        <div className="rounded-2xl border border-muted bg-card p-4 mt-6">
          <div className="h-4 w-32 bg-muted rounded mb-3" />
          <div className="space-y-2">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-16 bg-muted rounded-xl" />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}