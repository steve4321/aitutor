'use client';

import { useEffect, useRef, useState } from 'react';
import 'katex/dist/katex.min.css';
import { cn } from '@/lib/utils';

interface KatexRendererProps {
  latex: string;
  displayMode?: boolean;
  className?: string;
}

export function KatexRenderer({
  latex,
  displayMode = true,
  className,
}: KatexRendererProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState(false);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    if (containerRef.current) {
      import('katex').then((katex) => {
        try {
          katex.default.render(latex, containerRef.current!, {
            displayMode,
            throwOnError: false,
            trust: true,
          });
          setError(false);
          setLoaded(true);
        } catch (err) {
          if (containerRef.current) {
            containerRef.current.textContent = latex;
          }
          setError(true);
          setLoaded(true);
        }
      }).catch(() => {
        if (containerRef.current) {
          containerRef.current.textContent = latex;
        }
        setError(true);
        setLoaded(true);
      });
    }
  }, [latex, displayMode]);

  if (!loaded) {
    return (
      <span className={cn('animate-pulse text-muted-foreground', className)}>
        {latex}
      </span>
    );
  }

  return (
    <div
      ref={containerRef}
      className={cn(
        'overflow-x-auto py-2 text-gray-900',
        displayMode && 'text-center text-lg',
        error && 'text-red-500',
        className
      )}
    />
  );
}
