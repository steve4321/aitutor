'use client';

import dynamic from 'next/dynamic';
import { Suspense } from 'react';
import { Card } from '@/components/ui/card';
import { LoadingSkeleton, AnimationSkeleton } from '@/components/ui/loading-skeleton';
import { Play, Sparkles } from 'lucide-react';
import { renderWithLatex } from '@/lib/render-content';

const KatexRenderer = dynamic(
  () => import('@/components/math/katex-renderer').then((m) => ({ default: m.KatexRenderer })),
  {
    loading: () => <LoadingSkeleton className="h-6 w-24" />,
    ssr: false,
  }
);

const AnimationPlayer = dynamic(
  () => import('@/components/math/animation-player').then((m) => ({ default: m.AnimationPlayer })),
  {
    loading: () => <AnimationSkeleton />,
    ssr: false,
  }
);

export function FormulaCard({ title, latex, note }: { title?: string; latex: string; note?: string }) {
  return (
    <Card className="p-5 border-2 border-purple-200 dark:border-purple-800/50 bg-purple-50/50 dark:bg-purple-950/20">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-full bg-purple-500 flex items-center justify-center shrink-0">
          <span className="text-white font-bold text-lg">ƒ</span>
        </div>
        <div className="flex-1">
          {title && <h3 className="text-lg font-bold text-[var(--color-foreground)] mb-3">{renderWithLatex(title)}</h3>}
          <div className="bg-white dark:bg-slate-800 rounded-lg p-4 flex items-center justify-center">
            <Suspense fallback={<LoadingSkeleton className="h-12 w-48" />}>
              <KatexRenderer latex={latex} displayMode />
            </Suspense>
          </div>
          {note && (
            <p className="mt-2 text-sm text-[var(--color-muted-foreground)] italic">{note}</p>
          )}
        </div>
      </div>
    </Card>
  );
}

export function AnimationCard({
  title,
  url,
  animationType,
  thumbnailUrl,
  durationSec,
  description,
}: {
  title: string;
  url?: string;
  animationType?: 'manim' | 'lottie' | 'css' | 'canvas';
  thumbnailUrl?: string;
  durationSec?: number;
  description?: string;
}) {
  return (
    <Card className="overflow-hidden p-0">
      <div className="flex items-center gap-2 px-5 pt-4 pb-2">
        <div className="w-10 h-10 rounded-full bg-[var(--color-primary)] flex items-center justify-center shrink-0">
          <Play className="w-5 h-5 text-white" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-[var(--color-foreground)]">{renderWithLatex(title || '动画演示')}</h3>
          {description && (
            <p className="text-sm text-[var(--color-muted-foreground)] mt-0.5">{description}</p>
          )}
        </div>
      </div>
      <div className="px-4 pb-4">
        <Suspense fallback={<AnimationSkeleton />}>
          <AnimationPlayer
            url={url}
            title={title || '动画演示'}
            animationType={animationType}
            thumbnailUrl={thumbnailUrl}
            durationSec={durationSec}
          />
        </Suspense>
      </div>
    </Card>
  );
}

export function GeoGebraCard({ materialId, instructions, width, height }: { materialId?: string; instructions: string; width?: number; height?: number }) {
  const embedWidth = width ?? 800;
  const embedHeight = height ?? 500;
  return (
    <Card className="overflow-hidden">
      <div className="p-4">
        <div className="flex items-start gap-3 mb-3">
          <div className="w-10 h-10 rounded-full bg-indigo-500 flex items-center justify-center shrink-0">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-base font-bold text-[var(--color-foreground)]">GeoGebra 互动</h3>
            {instructions && <p className="text-sm text-[var(--color-muted-foreground)] mt-0.5">{instructions}</p>}
          </div>
        </div>
        {materialId ? (
          <iframe
            src={`https://www.geogebra.org/material/iframe/id/${materialId}/width/${embedWidth}/height/${embedHeight}`}
            width={embedWidth}
            height={embedHeight}
            className="w-full border-0 rounded-lg"
            title="GeoGebra"
            allowFullScreen
          />
        ) : (
          <div className="flex items-center justify-center bg-[var(--color-surface-muted)] rounded-lg p-8 text-sm text-[var(--color-muted-foreground)]">
            GeoGebra 组件加载中…
          </div>
        )}
      </div>
    </Card>
  );
}
