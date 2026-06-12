export default function Loading() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="mx-auto max-w-4xl px-4 py-8">
        <div className="h-8 w-24 bg-muted rounded mb-8" />
        <div className="grid gap-4 sm:grid-cols-2">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="h-48 bg-muted rounded-2xl" />
          ))}
        </div>
        <div className="h-40 bg-muted rounded-2xl mt-8" />
        <div className="h-40 bg-muted rounded-2xl mt-4" />
      </div>
    </div>
  );
}