'use client';

import { cn } from '@/lib/utils';
import { Loader2 } from 'lucide-react';
import type { PillarMastery } from '@/types/dashboard';

interface MasteryRadarProps {
  subjects: PillarMastery[];
  isLoading?: boolean;
  className?: string;
}

export function MasteryRadar({ subjects, isLoading = false, className }: MasteryRadarProps) {
  const maxRadius = 80;
  const center = 100;
  const levels = [0.2, 0.4, 0.6, 0.8, 1.0];

  const getPoint = (index: number, value: number) => {
    const angle = (Math.PI * 2 * index) / subjects.length - Math.PI / 2;
    const r = value * maxRadius;
    return {
      x: center + r * Math.cos(angle),
      y: center + r * Math.sin(angle),
    };
  };

  const points = subjects.map((s, i) => {
    const p = getPoint(i, s.mastery);
    return `${p.x},${p.y}`;
  }).join(' ');

  return (
    <div className={cn('rounded-xl border border-gray-200 bg-white p-4', className)}>
      <h3 className="mb-3 text-sm font-semibold text-gray-900">知识点掌握度</h3>
      {isLoading ? (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
        </div>
      ) : subjects.length < 3 ? (
        <div className="flex items-center justify-center py-8">
          <p className="text-sm text-gray-400">需要至少3个知识点才能展示雷达图</p>
        </div>
      ) : (
        <>
          <div className="flex items-center justify-center">
            <svg width="200" height="200" viewBox="0 0 200 200">
              {levels.map((level) => (
                <polygon
                  key={level}
                  points={subjects.map((_, i) => {
                    const p = getPoint(i, level);
                    return `${p.x},${p.y}`;
                  }).join(' ')}
                  fill="none"
                  stroke="#e5e7eb"
                  strokeWidth="1"
                />
              ))}

              {subjects.map((_, i) => {
                const start = { x: center, y: center };
                const end = getPoint(i, 1);
                return (
                  <line
                    key={i}
                    x1={start.x}
                    y1={start.y}
                    x2={end.x}
                    y2={end.y}
                    stroke="#e5e7eb"
                    strokeWidth="1"
                  />
                );
              })}

              <polygon
                points={points}
                fill="rgba(59, 130, 246, 0.2)"
                stroke="#3b82f6"
                strokeWidth="2"
              />

              {subjects.map((s, i) => {
                const labelPos = getPoint(i, 1.25);
                return (
                  <text
                    key={i}
                    x={labelPos.x}
                    y={labelPos.y}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    className="text-[10px] fill-gray-600"
                  >
                    {s.name}
                  </text>
                );
              })}
            </svg>
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            {subjects.map((s) => (
              <span
                key={s.name}
                className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-700"
              >
                <span
                  className="h-2 w-2 rounded-full"
                  style={{ backgroundColor: s.color }}
                />
                {s.name} {Math.round(s.mastery * 100)}%
              </span>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
