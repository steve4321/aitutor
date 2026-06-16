'use client';

import { useRef, useLayoutEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import 'katex/dist/katex.min.css';

interface KatexRendererProps {
  latex: string;
  displayMode?: boolean;
  className?: string;
}

interface KatexApi {
  render: (tex: string, element: HTMLElement, options?: object) => void;
}

export function KatexRenderer({
  latex,
  displayMode = true,
  className,
}: KatexRendererProps) {
  const containerRef = useRef<HTMLSpanElement>(null);
  const [katexLib, setKatexLib] = useState<KatexApi | null>(null);

  useLayoutEffect(() => {
    import('katex').then((mod) => {
      const api = (mod.default ?? mod) as KatexApi;
      setKatexLib(api);
    });
  }, []);

  useLayoutEffect(() => {
    if (!containerRef.current || !katexLib) return;
    const el = containerRef.current;
    el.innerHTML = '';
    try {
      katexLib.render(latex, el, {
        displayMode,
        throwOnError: false,
        trust: true,
      });
    } catch {
      el.textContent = latex;
    }
  }, [latex, displayMode, katexLib]);

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
