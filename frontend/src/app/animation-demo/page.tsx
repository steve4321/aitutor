'use client';

import { AnimationPlayer } from '@/components/math/animation-player';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

const ANIMATION_API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export default function AnimationDemoPage() {
  return (
    <div className="min-h-screen bg-[var(--color-background)] p-4 pb-24">
      <div className="mx-auto max-w-3xl">
        <div className="flex items-center gap-3 mb-6">
          <Link
            href="/home"
            className="flex h-9 w-9 items-center justify-center rounded-full hover:bg-[var(--color-primary-light)]"
          >
            <ArrowLeft className="h-5 w-5 text-[var(--color-foreground)]" />
          </Link>
          <h1 className="text-xl font-bold text-[var(--color-foreground)]">
            Math Animation Demo
          </h1>
        </div>

        <div className="space-y-8">
          <div>
            <h2 className="text-lg font-semibold text-[var(--color-foreground)] mb-3">
              Quadratic Function Transformation
            </h2>
            <p className="text-sm text-[var(--color-muted-foreground)] mb-4">
              y = x² → y = (x-2)² + 1 — shows vertex shift from (0,0) to (2,1) with Chinese narration
            </p>
            <AnimationPlayer
              url={`${ANIMATION_API_BASE.replace('/api/v1', '')}/static/animations/quadratic_transform.mp4`}
              title="Quadratic Function Graph Transformation"
              animationType="manim"
              durationSec={30}
            />
          </div>

          <div className="p-4 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)]">
            <h3 className="text-sm font-semibold text-[var(--color-foreground)] mb-2">
              Animation Pipeline
            </h3>
            <div className="text-xs text-[var(--color-muted-foreground)] space-y-1">
              <p>1. AI generates animation description JSON</p>
              <p>2. JSON → Manim CE Python script → MP4 video</p>
              <p>3. Edge TTS generates Chinese narration audio</p>
              <p>4. ffmpeg merges video + audio → final MP4 with narration</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
