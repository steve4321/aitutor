'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ChevronDown, ChevronUp, Check, X, BookOpen, Lightbulb, Target, FileText, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';
import { KatexRenderer } from '@/components/math/katex-renderer';
import type { PracticeProblem, LessonSection } from '@/types/course';

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
            return <IntroductionCard key={idx} content={section.content || ''} />;
          case 'concept':
            return <ConceptCard key={idx} title={section.title || ''} content={section.content || ''} />;
          case 'example':
            return <ExampleCard key={idx} problem={section.problem || ''} solution={section.solution || ''} />;
          case 'practice':
            return <PracticeCard key={idx} problems={section.problems || []} onAnswer={onAnswer} />;
          case 'summary':
            return <SummaryCard key={idx} content={section.content || ''} />;
          default:
            return null;
        }
      })}
    </div>
  );
}

function IntroductionCard({ content }: { content: string }) {
  return (
    <Card className="bg-[var(--color-primary-light)] border-2 border-[var(--color-primary)]/30 p-5">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-full bg-[var(--color-primary)] flex items-center justify-center shrink-0">
          <BookOpen className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-bold text-[var(--color-foreground)] mb-2">开篇引言</h3>
          <p className="text-base text-[var(--color-foreground)] leading-relaxed whitespace-pre-line">{content}</p>
        </div>
      </div>
    </Card>
  );
}

function ConceptCard({ title, content }: { title: string; content: string }) {
  return (
    <Card className="p-5">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-full bg-[var(--color-accent)] flex items-center justify-center shrink-0">
          <Lightbulb className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-bold text-[var(--color-foreground)] mb-2">{title || '核心概念'}</h3>
          <div className="text-base text-[var(--color-foreground)] leading-relaxed whitespace-pre-line">
            {renderWithLatex(content)}
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
