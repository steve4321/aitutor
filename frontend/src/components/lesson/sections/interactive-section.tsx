'use client';

import { useState, useCallback, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { VoiceRecorder } from '@/components/ui/voice-recorder';
import { Check, X, FileText, Volume2, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { renderWithLatex, stripLatexForSpeech } from '@/lib/render-content';
import { useChat } from '@/hooks/use-chat';
import { useTTS } from '@/hooks/use-tts';
import type { PracticeProblem } from '@/types/course';

export function PracticeCard({ problems, onAnswer }: { problems: PracticeProblem[]; onAnswer?: (idx: number, correct: boolean, answer?: string, problemId?: string) => void }) {
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

export function VoiceInputCard({ prompt, sessionId, subject }: { prompt: string; sessionId?: string | null; subject?: string }) {
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
