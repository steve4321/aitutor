'use client';

import { useState, useCallback, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { VoiceRecorder } from '@/components/ui/voice-recorder';
import { ChevronDown, ChevronUp, Check, X, BookOpen, Lightbulb, Target, FileText, Sparkles, Play, Volume2, Image, Table, ChevronRight, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { renderWithLatex, renderMarkdownWithLatex, stripLatexForSpeech } from '@/lib/render-content';
import { useChat } from '@/hooks/use-chat';
import { useTTS } from '@/hooks/use-tts';
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
  onAnswer?: (problemIndex: number, isCorrect: boolean, answer?: string, problemId?: string) => void;
  sessionId?: string | null;
  subject?: string;
}

export function LessonContent({ sections, onAnswer, sessionId, subject }: LessonContentProps) {
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
            return <VoiceInputCard key={idx} prompt={section.voicePrompt || ''} sessionId={sessionId} subject={subject} />;
          case 'illustration':
            return <IllustrationCard key={idx} title={section.title} description={section.content || ''} />;
          case 'audio':
            return <AudioBlockCard key={idx} url={section.audioUrl || ''} duration={section.audioDuration} transcript={section.audioTranscript} label={section.audioLabel} autoplay={section.audioAutoplay} />;
          case 'image':
            return <ImageBlockCard key={idx} url={section.imageUrl || ''} alt={section.imageAlt || ''} caption={section.imageCaption} />;
          case 'geogebra':
            return <GeoGebraCard key={idx} materialId={section.geogebraMaterialId} instructions={section.geogebraInstructions || ''} width={section.geogebraWidth} height={section.geogebraHeight} />;
          case 'divider':
            return <DividerCard key={idx} variant={section.dividerVariant} label={section.dividerLabel} />;
          case 'code':
            return <CodeBlockCard key={idx} code={section.codeContent || ''} language={section.codeLanguage} title={section.title} />;
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
          <h3 className="text-lg font-bold text-[var(--color-foreground)] mb-2">{renderWithLatex(title || '开篇引言')}</h3>
          <div className="text-base text-[var(--color-foreground)] leading-relaxed whitespace-pre-line">{renderWithLatex(content)}</div>
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
          <h3 className="text-lg font-bold text-[var(--color-foreground)] mb-2">{renderWithLatex(title || '核心概念')}</h3>
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

function PracticeCard({ problems, onAnswer }: { problems: PracticeProblem[]; onAnswer?: (idx: number, correct: boolean, answer?: string, problemId?: string) => void }) {
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

function PracticeProblemItem({ problem, index, onAnswer }: { problem: PracticeProblem; index: number; onAnswer?: (idx: number, correct: boolean, answer?: string, problemId?: string) => void }) {
  const [selected, setSelected] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const isCorrect = selected === problem.answer;

  const handleSubmit = () => {
    if (!selected) return;
    setSubmitted(true);
    onAnswer?.(index, isCorrect, selected, problem.problem_id);
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
              {renderWithLatex(opt)}
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
          <p className="text-base text-[var(--color-foreground)] leading-relaxed whitespace-pre-line">{renderWithLatex(content)}</p>
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
          <h3 className="text-lg font-bold text-[var(--color-foreground)]">{renderWithLatex(title || '动画演示')}</h3>
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
          {title && <h3 className="text-lg font-bold text-[var(--color-foreground)] mb-3">{renderWithLatex(title)}</h3>}
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

function TableCard({ title, headers, rows }: { title?: string; headers: string[]; rows: string[][] }) {
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

function VoiceInputCard({ prompt, sessionId, subject }: { prompt: string; sessionId?: string | null; subject?: string }) {
  const [rounds, setRounds] = useState<Array<{ user: string; ai: string | null; speaking?: boolean }>>([]);
  const [currentError, setCurrentError] = useState<string | null>(null);
  const [isLoadingAi, setIsLoadingAi] = useState(false);

  const { speak, isSpeaking, loading: ttsLoading, stop: stopSpeaking } = useTTS();
  const { messages, send } = useChat({
    sessionId: sessionId ?? undefined,
    autoCreate: false,
    subject: subject ?? 'math',
  });

  const handlePromptRead = useCallback(() => {
    if (isSpeaking) {
      stopSpeaking();
    } else if (!ttsLoading) {
      speak(stripLatexForSpeech(prompt));
    }
  }, [prompt, isSpeaking, ttsLoading, stopSpeaking, speak]);

  const handleTranscript = useCallback(
    async (text: string) => {
      setCurrentError(null);
      setRounds((prev) => [...prev, { user: text, ai: null }]);
      setIsLoadingAi(true);
      try {
        await send(text);
      } catch (err) {
        setCurrentError(err instanceof Error ? err.message : '发送失败，请重试');
      } finally {
        setIsLoadingAi(false);
      }
    },
    [send]
  );

  const handlePlayAiResponse = useCallback(
    (text: string) => {
      speak(stripLatexForSpeech(text));
    },
    [speak]
  );

  const lastAiMessage = messages.length > 0 ? messages[messages.length - 1] : null;
  useEffect(() => {
    if (lastAiMessage && lastAiMessage.role === 'assistant') {
      setRounds((prev) => {
        if (prev.length === 0) return prev;
        const lastRound = prev[prev.length - 1];
        if (lastRound.ai !== null) return prev;
        const updated = [...prev];
        updated[updated.length - 1] = { ...lastRound, ai: lastAiMessage.content };
        return updated;
      });
    }
  }, [lastAiMessage]);

  return (
    <Card className="p-4 border-2 border-green-200 dark:border-green-800/50 bg-green-50/50 dark:bg-green-950/20">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-full bg-green-500 flex items-center justify-center shrink-0">
          <Volume2 className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-sm font-semibold text-green-700 dark:text-green-400">语音互动</h3>
            <button
              onClick={handlePromptRead}
              disabled={ttsLoading}
              className={cn(
                'flex items-center gap-1 text-xs px-2 py-0.5 rounded-full transition-all',
                ttsLoading && 'opacity-50 cursor-wait',
                isSpeaking
                  ? 'bg-green-200 dark:bg-green-800 text-green-700 dark:text-green-300'
                  : 'bg-green-100 dark:bg-green-900 text-green-600 dark:text-green-400 hover:bg-green-200 dark:hover:bg-green-800'
              )}
            >
              <Volume2 className="w-3 h-3" />
              {ttsLoading ? '加载中...' : isSpeaking ? '停止' : '朗读'}
            </button>
          </div>
          <p className="text-base text-[var(--color-foreground)] leading-relaxed">{renderWithLatex(prompt)}</p>
        </div>
      </div>

      <div className="mt-4 flex flex-col items-center gap-3">
        <VoiceRecorder
          onTranscript={handleTranscript}
          size="lg"
          showTranscript
        />

        {isLoadingAi && (
          <div className="flex items-center gap-2 text-sm text-[var(--color-muted-foreground)]">
            <Loader2 className="w-4 h-4 animate-spin" />
            AI 思考中...
          </div>
        )}

        {currentError && (
          <div className="text-sm text-[var(--color-danger)]">{currentError}</div>
        )}

        {rounds.map((round, idx) => (
          <div key={idx} className="w-full space-y-2">
            <div className="max-w-[85%] ml-auto rounded-2xl rounded-tr-sm px-4 py-2.5 text-sm bg-[var(--color-primary)] text-white">
              {round.user}
            </div>
            {round.ai && (
              <div className="max-w-[85%] mr-auto rounded-2xl rounded-tl-sm px-4 py-2.5 text-sm bg-[var(--color-surface-muted)] text-[var(--color-foreground)]">
                <div className="flex items-start gap-2">
                  <span className="flex-1">{round.ai}</span>
                  <button
                    onClick={() => handlePlayAiResponse(round.ai!)}
                    className="shrink-0 p-1 rounded-full hover:bg-green-100 dark:hover:bg-green-900 transition-colors"
                    aria-label="播放AI回复"
                  >
                    <Volume2 className="w-4 h-4 text-green-600 dark:text-green-400" />
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
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
          {title && <h3 className="text-sm font-semibold text-amber-700 dark:text-amber-400 mb-1">{renderWithLatex(title)}</h3>}
          <p className="text-sm text-[var(--color-foreground)] leading-relaxed">{description}</p>
        </div>
      </div>
    </Card>
  );
}

function AudioBlockCard({ url, duration, transcript, label, autoplay }: { url: string; duration?: number; transcript?: string; label?: string; autoplay?: boolean }) {
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

function ImageBlockCard({ url, alt, caption }: { url: string; alt: string; caption?: string }) {
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

function GeoGebraCard({ materialId, instructions, width, height }: { materialId?: string; instructions: string; width?: number; height?: number }) {
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

function DividerCard({ variant, label }: { variant?: 'line' | 'spacing' | 'dots' | 'label'; label?: string }) {
  if (variant === 'spacing') return <div className="h-6" />;
  if (variant === 'dots') return <div className="flex items-center justify-center gap-1 py-4"><span className="w-1.5 h-1.5 rounded-full bg-[var(--color-muted-foreground)]" /><span className="w-1.5 h-1.5 rounded-full bg-[var(--color-muted-foreground)]" /><span className="w-1.5 h-1.5 rounded-full bg-[var(--color-muted-foreground)]" /></div>;
  if (variant === 'label' && label) return <div className="flex items-center gap-3 py-2"><hr className="flex-1 border-[var(--color-border)]" /><span className="text-xs text-[var(--color-muted-foreground)] font-medium">{label}</span><hr className="flex-1 border-[var(--color-border)]" /></div>;
  return <hr className="border-[var(--color-border)]" />;
}

function CodeBlockCard({ code, language, title }: { code: string; language?: string; title?: string }) {
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
