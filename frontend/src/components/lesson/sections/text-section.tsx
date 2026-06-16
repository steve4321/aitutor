'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ChevronDown, ChevronUp, BookOpen, Lightbulb, Target, Sparkles, Volume2, Image, Table, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import { renderWithLatex, renderMarkdownWithLatex } from '@/lib/render-content';

export function IntroductionCard({ content, title }: { content: string; title?: string }) {
  return (
    <Card className="bg-[var(--color-primary-light)] border-2 border-[var(--color-primary)]/30 p-5">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-full bg-[var(--color-primary)] flex items-center justify-center shrink-0">
          <BookOpen className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-bold text-[var(--color-foreground)] mb-2">{renderWithLatex(title || '开篇引言')}</h3>
          <div className="text-base text-[var(--color-foreground)] leading-relaxed whitespace-pre-line">{renderWithLatex(content)}</div>
        </div>
      </div>
    </Card>
  );
}

export function ConceptCard({ title, content, variant }: { title: string; content: string; variant?: string }) {
  const isCallout = variant === 'callout';
  return (
    <Card className={cn("p-5", isCallout && "bg-blue-50 dark:bg-blue-950/30 border-2 border-blue-200 dark:border-blue-800/50")}>
      <div className="flex items-start gap-3">
        <div className={cn(
          "w-10 h-10 rounded-full flex items-center justify-center shrink-0",
          isCallout ? "bg-blue-500" : "bg-[var(--color-accent)]"
        )}>
          <Lightbulb className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-bold text-[var(--color-foreground)] mb-2">{renderWithLatex(title || '核心概念')}</h3>
          <div className="text-base text-[var(--color-foreground)] leading-relaxed prose prose-slate dark:prose-invert max-w-none">
            {renderMarkdownWithLatex(content)}
          </div>
        </div>
      </div>
    </Card>
  );
}

export function ExampleCard({ problem, solution }: { problem: string; solution: string }) {
  const [showSolution, setShowSolution] = useState(false);
  return (
    <Card className="p-5 border-2 border-[var(--color-secondary)]/30">
      <div className="flex items-start gap-3 mb-3">
        <div className="w-10 h-10 rounded-full bg-[var(--color-secondary)] flex items-center justify-center shrink-0">
          <Target className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-bold text-[var(--color-foreground)] mb-2">例题</h3>
          <div className="text-base text-[var(--color-foreground)] leading-relaxed mb-3">
            {renderWithLatex(problem)}
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowSolution(!showSolution)}
            className="gap-2"
          >
            {showSolution ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            {showSolution ? '隐藏解析' : '查看解析'}
          </Button>
          {showSolution && (
            <div className="mt-3 p-4 rounded-xl bg-[var(--color-secondary-light)] border border-[var(--color-secondary)]/20">
              <p className="text-sm font-semibold text-[var(--color-secondary)] mb-1">解析</p>
              <div className="text-base text-[var(--color-foreground)] leading-relaxed whitespace-pre-line">
                {renderWithLatex(solution)}
              </div>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}

export function SummaryCard({ content }: { content: string }) {
  return (
    <Card className="bg-gradient-to-br from-[var(--color-success-light)] to-[var(--color-primary-light)] border-2 border-[var(--color-success)]/30 p-5">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-full bg-[var(--color-success)] flex items-center justify-center shrink-0">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-bold text-[var(--color-foreground)] mb-2">本节小结</h3>
          <p className="text-base text-[var(--color-foreground)] leading-relaxed whitespace-pre-line">{renderWithLatex(content)}</p>
        </div>
      </div>
    </Card>
  );
}

export function ExpandableCard({ title, content }: { title: string; content: string }) {
  const [open, setOpen] = useState(false);
  return (
    <Card className="overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-3 p-4 text-left hover:bg-[var(--color-surface-muted)] transition-colors"
      >
        <ChevronRight className={cn("w-5 h-5 text-[var(--color-muted-foreground)] transition-transform", open && "rotate-90")} />
        <span className="text-base font-semibold text-[var(--color-foreground)]">{renderWithLatex(title)}</span>
      </button>
      {open && (
        <div className="px-5 pb-4 text-base text-[var(--color-foreground)] leading-relaxed prose prose-slate dark:prose-invert max-w-none">
          {renderMarkdownWithLatex(content)}
        </div>
      )}
    </Card>
  );
}

export function TableCard({ title, headers, rows }: { title?: string; headers: string[]; rows: string[][] }) {
  return (
    <Card className="overflow-hidden">
      {title && (
        <div className="flex items-center gap-2 px-5 pt-4 pb-2">
          <Table className="w-5 h-5 text-[var(--color-primary)]" />
          <h3 className="text-lg font-bold text-[var(--color-foreground)]">{renderWithLatex(title)}</h3>
        </div>
      )}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-[var(--color-surface-muted)]">
              {headers.map((h, i) => (
                <th key={i} className="px-3 py-2 text-left font-semibold text-[var(--color-foreground)] border-b border-[var(--color-border)]">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, ri) => (
              <tr key={ri} className={cn(ri % 2 === 1 && "bg-[var(--color-surface-muted)]/50")}>
                {row.map((cell, ci) => (
                  <td key={ci} className="px-3 py-2 text-[var(--color-foreground)] border-b border-[var(--color-border)]/50">
                    {renderWithLatex(cell)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

export function IllustrationCard({ title, description }: { title?: string; description: string }) {
  return (
    <Card className="p-4 border-2 border-amber-200 dark:border-amber-800/50 bg-amber-50/50 dark:bg-amber-950/20">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-full bg-amber-500 flex items-center justify-center shrink-0">
          <Image className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          {title && <h3 className="text-sm font-semibold text-amber-700 dark:text-amber-400 mb-1">{renderWithLatex(title)}</h3>}
          <p className="text-sm text-[var(--color-foreground)] leading-relaxed">{description}</p>
        </div>
      </div>
    </Card>
  );
}

export function AudioBlockCard({ url, duration, transcript, label, autoplay }: { url: string; duration?: number; transcript?: string; label?: string; autoplay?: boolean }) {
  if (!url) return null;
  return (
    <Card className="p-4 border-2 border-teal-200 dark:border-teal-800/50 bg-teal-50/50 dark:bg-teal-950/20">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-full bg-teal-500 flex items-center justify-center shrink-0">
          <Volume2 className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-teal-700 dark:text-teal-400 mb-1">{label || '音频播放'}</h3>
          <audio
            controls
            src={url}
            autoPlay={autoplay}
            className="w-full h-10 mt-1"
          />
          {duration != null && (
            <p className="text-xs text-[var(--color-muted-foreground)] mt-1">时长: {Math.floor(duration / 60)}:{String(duration % 60).padStart(2, '0')}</p>
          )}
          {transcript && (
            <details className="mt-2">
              <summary className="text-xs text-[var(--color-muted-foreground)] cursor-pointer">显示文本</summary>
              <p className="mt-1 text-sm text-[var(--color-foreground)] leading-relaxed whitespace-pre-line">{transcript}</p>
            </details>
          )}
        </div>
      </div>
    </Card>
  );
}

export function ImageBlockCard({ url, alt, caption }: { url: string; alt: string; caption?: string }) {
  if (!url) return null;
  return (
    <Card className="overflow-hidden p-0">
      <img src={url} alt={alt} className="w-full object-contain" loading="lazy" />
      {caption && (
        <p className="px-4 py-2 text-sm text-[var(--color-muted-foreground)] border-t border-[var(--color-border)]">{caption}</p>
      )}
    </Card>
  );
}

export function DividerCard({ variant, label }: { variant?: 'line' | 'spacing' | 'dots' | 'label'; label?: string }) {
  if (variant === 'spacing') return <div className="h-6" />;
  if (variant === 'dots') return <div className="flex items-center justify-center gap-1 py-4"><span className="w-1.5 h-1.5 rounded-full bg-[var(--color-muted-foreground)]" /><span className="w-1.5 h-1.5 rounded-full bg-[var(--color-muted-foreground)]" /><span className="w-1.5 h-1.5 rounded-full bg-[var(--color-muted-foreground)]" /></div>;
  if (variant === 'label' && label) return <div className="flex items-center gap-3 py-2"><hr className="flex-1 border-[var(--color-border)]" /><span className="text-xs text-[var(--color-muted-foreground)] font-medium">{label}</span><hr className="flex-1 border-[var(--color-border)]" /></div>;
  return <hr className="border-[var(--color-border)]" />;
}

export function CodeBlockCard({ code, language, title }: { code: string; language?: string; title?: string }) {
  return (
    <Card className="overflow-hidden">
      {(title || language) && (
        <div className="flex items-center justify-between px-4 py-2 bg-[var(--color-surface-muted)] border-b border-[var(--color-border)]">
          {title && <span className="text-sm font-medium text-[var(--color-foreground)]">{title}</span>}
          {language && <span className="text-xs text-[var(--color-muted-foreground)] uppercase">{language}</span>}
        </div>
      )}
      <pre className="p-4 overflow-x-auto text-sm leading-relaxed bg-slate-950 text-slate-100 dark:bg-slate-900 dark:text-slate-200">
        <code>{code}</code>
      </pre>
    </Card>
  );
}
