'use client';

import { useRef, useLayoutEffect } from 'react';
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
  const containerRef = useRef<HTMLSpanElement>(null);

  useLayoutEffect(() => {
    if (!containerRef.current) return;
    const el = containerRef.current;
    el.innerHTML = '';
    try {
      katex.render(latex, el, {
        displayMode,
        throwOnError: false,
        trust: true,
      });
    } catch {
      el.textContent = latex;
    }
  }, [latex, displayMode]);

  return (
    <span
      ref={containerRef}
      className={cn(
        displayMode ? 'block text-center' : 'inline',
        className
      )}
    />
  );
}
