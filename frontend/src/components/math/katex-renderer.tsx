'use client';

import { useEffect, useRef } from 'react';
import katex from 'katex';
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

  useEffect(() => {
    if (containerRef.current) {
      try {
        katex.render(latex, containerRef.current, {
          displayMode,
          throwOnError: false,
          trust: true,
        });
      } catch (error) {
        if (containerRef.current) {
          containerRef.current.textContent = latex;
        }
      }
    }
  }, [latex, displayMode]);

  return (
    <div
      ref={containerRef}
      className={cn(
        'overflow-x-auto py-2 text-gray-900',
        displayMode && 'text-center text-lg',
        className
      )}
    />
  );
}
