'use client';

import { useState } from 'react';
import dynamic from 'next/dynamic';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ChevronDown, ChevronUp, Check, X, BookOpen, Lightbulb, Target, FileText, Sparkles, Play, Volume2, Image, Table, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { PracticeProblem, LessonSection } from '@/types/course';

const KatexRenderer = dynamic(
  () => import('@/components/math/katex-renderer').then((m) => ({ default: m.KatexRenderer })),
  {
    loading: () => <span className="text-muted-foreground animate-pulse">…</span>,
    ssr: false,
  }
);

const AnimationPlayer = dynamic(
  () => import('@/components/math/animation-player').then((m) => ({ default: m.AnimationPlayer })),
  {
    loading: () => (
      <div className="aspect-video bg-[#1a1a2e] rounded-xl flex items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-white/20 border-t-white" />
      </div>
    ),
    ssr: false,
  }
);

interface LessonContentProps {
  sections: LessonSection[];
  onAnswer?: (problemIndex: number, isCorrect: boolean) => void;
}

export function LessonContent({ sections, onAnswer }: LessonContentProps) {
  return (
    <div className="space-y-4">
      {sections.map((section, idx) => {
        switch (section.type) {
          case 'introduction':
            return <IntroductionCard key={idx} content={section.content || ''} title={section.title} />;
          case 'concept':
          case 'text':
            return <ConceptCard key={idx} title={section.title || ''} content={section.content || ''} variant={section.variant} />;
          case 'example':
            return <ExampleCard key={idx} problem={section.problem || ''} solution={section.solution || ''} />;
          case 'practice':
            return <PracticeCard key={idx} problems={section.problems || []} onAnswer={onAnswer} />;
          case 'summary':
            return <SummaryCard key={idx} content={section.content || ''} />;
          case 'animation':
            return (
              <AnimationCard
                key={idx}
                title={section.title || ''}
                url={section.animationUrl}
                animationType={section.animationType}
                thumbnailUrl={section.thumbnailUrl}
                durationSec={section.durationSec}
                description={section.content}
              />
            );
          case 'formula':
            return <FormulaCard key={idx} title={section.title} latex={section.content || ''} note={section.note} />;
          case 'expandable':
            return <ExpandableCard key={idx} title={section.title || '展开查看'} content={section.content || ''} />;
          case 'interactive_table':
            return <TableCard key={idx} title={section.title} headers={section.tableHeaders || []} rows={section.tableRows || []} />;
          case 'voice_input':
            return <VoiceInputCard key={idx} prompt={section.voicePrompt || ''} />;
          case 'illustration':
            return <IllustrationCard key={idx} title={section.title} description={section.content || ''} />;
          default:
            return null;
        }
      })}
    </div>
  );
}

function IntroductionCard({ content, title }: { content: string; title?: string }) {
  return (
    <Card className="bg-[var(--color-primary-light)] border-2 border-[var(--color-primary)]/30 p-5">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-full bg-[var(--color-primary)] flex items-center justify-center shrink-0">
          <BookOpen className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-bold text-[var(--color-foreground)] mb-2">{title || '开篇引言'}</h3>
          <p className="text-base text-[var(--color-foreground)] leading-relaxed whitespace-pre-line">{content}</p>
        </div>
      </div>
    </Card>
  );
}

function ConceptCard({ title, content, variant }: { title: string; content: string; variant?: string }) {
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
          <h3 className="text-lg font-bold text-[var(--color-foreground)] mb-2">{title || '核心概念'}</h3>
          <div className="text-base text-[var(--color-foreground)] leading-relaxed prose prose-slate dark:prose-invert max-w-none">
            {renderMarkdownWithLatex(content)}
          </div>
        </div>
      </div>
    </Card>
  );
}

function ExampleCard({ problem, solution }: { problem: string; solution: string }) {
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

function PracticeCard({ problems, onAnswer }: { problems: PracticeProblem[]; onAnswer?: (idx: number, correct: boolean) => void }) {
  return (
    <Card className="p-5 border-2 border-[var(--color-warning)]/30 bg-[var(--color-warning-light)]/30">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-10 h-10 rounded-full bg-[var(--color-warning)] flex items-center justify-center">
          <FileText className="w-5 h-5 text-white" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-[var(--color-foreground)]">课堂练习</h3>
          <p className="text-sm text-[var(--color-muted-foreground)]">共 {problems.length} 题</p>
        </div>
      </div>
      <div className="space-y-3">
        {problems.map((p, idx) => (
          <PracticeProblemItem key={idx} problem={p} index={idx} onAnswer={onAnswer} />
        ))}
      </div>
    </Card>
  );
}

function PracticeProblemItem({ problem, index, onAnswer }: { problem: PracticeProblem; index: number; onAnswer?: (idx: number, correct: boolean) => void }) {
  const [selected, setSelected] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const isCorrect = selected === problem.answer;

  const handleSubmit = () => {
    if (!selected) return;
    setSubmitted(true);
    onAnswer?.(index, isCorrect);
  };

  return (
    <div className="bg-[var(--color-surface)] rounded-xl p-4 border border-[var(--color-border)]">
      <div className="flex items-start gap-2 mb-3">
        <span className="shrink-0 w-6 h-6 rounded-full bg-[var(--color-primary)] text-white text-sm font-bold flex items-center justify-center">
          {index + 1}
        </span>
        <div className="flex-1 text-base text-[var(--color-foreground)]">
          {renderWithLatex(problem.question)}
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2 mb-3">
        {problem.options.map((opt, i) => {
          const optKey = String.fromCharCode(65 + i);
          const isSelected = selected === optKey;
          const isCorrectAnswer = submitted && optKey === problem.answer;
          const isWrongSelected = submitted && isSelected && !isCorrect;
          return (
            <button
              key={i}
              onClick={() => !submitted && setSelected(optKey)}
              disabled={submitted}
              className={cn(
                'p-3 rounded-lg border-2 text-left text-sm transition-all min-h-[44px]',
                !submitted && !isSelected && 'border-[var(--color-border)] hover:border-[var(--color-primary)] bg-[var(--color-surface)]',
                !submitted && isSelected && 'border-[var(--color-primary)] bg-[var(--color-primary-light)]',
                isCorrectAnswer && 'border-[var(--color-success)] bg-[var(--color-success-light)]',
                isWrongSelected && 'border-[var(--color-danger)] bg-[var(--color-danger-light)]',
                submitted && !isSelected && !isCorrectAnswer && 'border-[var(--color-border)] opacity-50'
              )}
            >
              <span className="font-bold mr-2">{optKey}.</span>
              {opt}
              {isCorrectAnswer && <Check className="inline w-4 h-4 ml-2 text-[var(--color-success)]" />}
              {isWrongSelected && <X className="inline w-4 h-4 ml-2 text-[var(--color-danger)]" />}
            </button>
          );
        })}
      </div>
      {!submitted ? (
        <Button onClick={handleSubmit} disabled={!selected} size="sm" className="w-full">
          提交答案
        </Button>
      ) : (
        <div className={cn(
          'p-3 rounded-lg text-sm font-medium',
          isCorrect ? 'bg-[var(--color-success-light)] text-[var(--color-success)]' : 'bg-[var(--color-danger-light)] text-[var(--color-danger)]'
        )}>
          {isCorrect ? '答对了！' : `答错了，正确答案是 ${problem.answer}`}
        </div>
      )}
    </div>
  );
}

function SummaryCard({ content }: { content: string }) {
  return (
    <Card className="bg-gradient-to-br from-[var(--color-success-light)] to-[var(--color-primary-light)] border-2 border-[var(--color-success)]/30 p-5">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-full bg-[var(--color-success)] flex items-center justify-center shrink-0">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-bold text-[var(--color-foreground)] mb-2">本节小结</h3>
          <p className="text-base text-[var(--color-foreground)] leading-relaxed whitespace-pre-line">{content}</p>
        </div>
      </div>
    </Card>
  );
}

function AnimationCard({
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
          <h3 className="text-lg font-bold text-[var(--color-foreground)]">{title || '动画演示'}</h3>
          {description && (
            <p className="text-sm text-[var(--color-muted-foreground)] mt-0.5">{description}</p>
          )}
        </div>
      </div>
      <div className="px-4 pb-4">
        <AnimationPlayer
          url={url}
          title={title || '动画演示'}
          animationType={animationType}
          thumbnailUrl={thumbnailUrl}
          durationSec={durationSec}
        />
      </div>
    </Card>
  );
}

function FormulaCard({ title, latex, note }: { title?: string; latex: string; note?: string }) {
  return (
    <Card className="p-5 border-2 border-purple-200 dark:border-purple-800/50 bg-purple-50/50 dark:bg-purple-950/20">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-full bg-purple-500 flex items-center justify-center shrink-0">
          <span className="text-white font-bold text-lg">ƒ</span>
        </div>
        <div className="flex-1">
          {title && <h3 className="text-lg font-bold text-[var(--color-foreground)] mb-3">{title}</h3>}
          <div className="bg-white dark:bg-slate-800 rounded-lg p-4 flex items-center justify-center">
            <KatexRenderer latex={latex} displayMode />
          </div>
          {note && (
            <p className="mt-2 text-sm text-[var(--color-muted-foreground)] italic">{note}</p>
          )}
        </div>
      </div>
    </Card>
  );
}

function ExpandableCard({ title, content }: { title: string; content: string }) {
  const [open, setOpen] = useState(false);
  return (
    <Card className="overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-3 p-4 text-left hover:bg-[var(--color-surface-muted)] transition-colors"
      >
        <ChevronRight className={cn("w-5 h-5 text-[var(--color-muted-foreground)] transition-transform", open && "rotate-90")} />
        <span className="text-base font-semibold text-[var(--color-foreground)]">{title}</span>
      </button>
      {open && (
        <div className="px-5 pb-4 text-base text-[var(--color-foreground)] leading-relaxed prose prose-slate dark:prose-invert max-w-none">
          {renderMarkdownWithLatex(content)}
        </div>
      )}
    </Card>
  );
}

function TableCard({ title, headers, rows }: { title?: string; headers: string[]; rows: string[][] }) {
  return (
    <Card className="overflow-hidden">
      {title && (
        <div className="flex items-center gap-2 px-5 pt-4 pb-2">
          <Table className="w-5 h-5 text-[var(--color-primary)]" />
          <h3 className="text-lg font-bold text-[var(--color-foreground)]">{title}</h3>
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

function VoiceInputCard({ prompt }: { prompt: string }) {
  return (
    <Card className="p-4 border-2 border-green-200 dark:border-green-800/50 bg-green-50/50 dark:bg-green-950/20">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-full bg-green-500 flex items-center justify-center shrink-0">
          <Volume2 className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-green-700 dark:text-green-400 mb-1">语音互动</h3>
          <p className="text-base text-[var(--color-foreground)] leading-relaxed">{prompt}</p>
          <p className="mt-2 text-xs text-[var(--color-muted-foreground)]">（语音输入功能开发中）</p>
        </div>
      </div>
    </Card>
  );
}

function IllustrationCard({ title, description }: { title?: string; description: string }) {
  return (
    <Card className="p-4 border-2 border-amber-200 dark:border-amber-800/50 bg-amber-50/50 dark:bg-amber-950/20">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-full bg-amber-500 flex items-center justify-center shrink-0">
          <Image className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          {title && <h3 className="text-sm font-semibold text-amber-700 dark:text-amber-400 mb-1">{title}</h3>}
          <p className="text-sm text-[var(--color-foreground)] leading-relaxed">{description}</p>
        </div>
      </div>
    </Card>
  );
}

function renderMarkdownWithLatex(text: string): React.ReactNode {
  if (!text) return null;
  const lines = text.split('\n');
  return (
    <>
      {lines.map((line, li) => {
        if (!line.trim()) return <br key={li} />;
        if (line.startsWith('## ')) return <h2 key={li} className="text-xl font-bold mt-4 mb-2">{renderWithLatex(line.slice(3))}</h2>;
        if (line.startsWith('### ')) return <h3 key={li} className="text-lg font-semibold mt-3 mb-1">{renderWithLatex(line.slice(4))}</h3>;
        if (line.startsWith('> ')) return <blockquote key={li} className="border-l-4 border-blue-400 pl-3 my-2 text-[var(--color-muted-foreground)] italic">{renderWithLatex(line.slice(2))}</blockquote>;
        if (line.startsWith('- ') || line.startsWith('• ')) return <li key={li} className="ml-4">{renderWithLatex(line.slice(2))}</li>;
        if (line.startsWith('| ') && line.endsWith('|')) {
          const cells = line.split('|').filter(Boolean).map(c => c.trim());
          return <div key={li} className="flex gap-2 py-1 border-b border-[var(--color-border)]/30 text-sm">{cells.map((c, ci) => <span key={ci} className="flex-1">{renderWithLatex(c)}</span>)}</div>;
        }
        if (line.startsWith('**') && line.endsWith('**')) return <p key={li} className="font-bold mt-2">{renderWithLatex(line.slice(2, -2))}</p>;
        return <p key={li} className="mb-1">{renderWithLatex(line)}</p>;
      })}
    </>
  );
}

function renderWithLatex(text: string): React.ReactNode {
  if (!text) return null;
  const parts: React.ReactNode[] = [];
  let lastIdx = 0;
  const regex = /\$([^$]+)\$/g;
  let match;
  let key = 0;
  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIdx) {
      parts.push(text.slice(lastIdx, match.index));
    }
    parts.push(<KatexRenderer key={`latex-${key++}`} latex={match[1]} />);
    lastIdx = regex.lastIndex;
  }
  if (lastIdx < text.length) {
    parts.push(text.slice(lastIdx));
  }
  return <>{parts}</>;
}
