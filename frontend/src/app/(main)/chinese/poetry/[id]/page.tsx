'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Feather, ChevronLeft, Loader2, Send, CheckCircle, XCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';

interface PoetryPoem {
  id: string;
  title: string;
  poet: string;
  dynasty: string;
  full_text: string;
  theme: string;
  background?: string;
  imagery_analysis?: string;
  artistic_techniques?: string;
  comprehension_questions?: Array<{ question: string; hint?: string }>;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export default function PoetryDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const [poemId, setPoemId] = useState<string | null>(null);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [dictationAnswers, setDictationAnswers] = useState<Record<number, string>>({});
  const [dictationResults, setDictationResults] = useState<Record<number, boolean>>({});

  useEffect(() => {
    params.then((p) => setPoemId(p.id));
  }, [params]);

  const { data: poem, isLoading: poemLoading } = useQuery({
    queryKey: ['chinese', 'poetry', 'poem', poemId],
    queryFn: () => api.get<PoetryPoem>(`/chinese/poetry/${poemId}`),
    enabled: !!poemId,
  });

  const chatMutation = useMutation({
    mutationFn: (body: { poem_id: string; message: string; history: ChatMessage[] }) =>
      api.post<{ response: string }>('/chinese/poetry/chat', body),
    onSuccess: (data) => {
      setChatMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.response },
      ]);
    },
  });

  const handleSendChat = () => {
    if (!chatInput.trim() || !poem) return;
    const userMessage = chatInput.trim();
    setChatMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setChatInput('');
    chatMutation.mutate({
      poem_id: poem.id,
      message: userMessage,
      history: chatMessages,
    });
  };

  const handleDictationCheck = () => {
    if (!poem) return;
    const lines = poem.full_text.split('\n');
    const results: Record<number, boolean> = {};
    lines.forEach((line, index) => {
      const userAnswer = dictationAnswers[index] || '';
      const isCorrect = userAnswer === line;
      results[index] = isCorrect;
    });
    setDictationResults(results);
  };

  if (poemLoading) {
    return (
      <div className="space-y-6">
        <div className="mx-auto max-w-3xl px-4 py-8">
          <header className="mb-6 flex items-center gap-4">
            <Link
              href="/chinese/poetry"
              className="flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm hover:shadow-md dark:bg-slate-800"
            >
              <ChevronLeft className="h-5 w-5 text-slate-600 dark:text-slate-300" />
            </Link>
            <div className="flex items-center gap-3">
              <Feather className="h-7 w-7 text-emerald-600 dark:text-emerald-400" />
              <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">诗词赏析</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400">加载中...</p>
              </div>
            </div>
          </header>
          <div className="flex flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-12 dark:border-slate-700 dark:bg-slate-800">
            <Loader2 className="h-8 w-8 animate-spin text-emerald-600" />
            <p className="mt-4 text-slate-500 dark:text-slate-400">诗词加载中...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!poem) {
    return (
      <div className="space-y-6">
        <div className="mx-auto max-w-3xl px-4 py-8">
          <header className="mb-6 flex items-center gap-4">
            <Link
              href="/chinese/poetry"
              className="flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm hover:shadow-md dark:bg-slate-800"
            >
              <ChevronLeft className="h-5 w-5 text-slate-600 dark:text-slate-300" />
            </Link>
            <div className="flex items-center gap-3">
              <Feather className="h-7 w-7 text-emerald-600 dark:text-emerald-400" />
              <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">诗词赏析</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400">诗词未找到</p>
              </div>
            </div>
          </header>
          <div className="flex flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-12 dark:border-slate-700 dark:bg-slate-800">
            <Feather className="h-16 w-16 text-slate-300 dark:text-slate-600" />
            <h2 className="mb-2 text-xl font-semibold text-slate-900 dark:text-white">诗词未找到</h2>
            <p className="mb-8 text-center text-slate-500 dark:text-slate-400">
              请返回重新选择诗词
            </p>
            <Link
              href="/chinese/poetry"
              className="flex items-center gap-2 rounded-xl bg-emerald-600 px-6 py-3 font-medium text-white transition-all hover:bg-emerald-700"
            >
              返回诗词列表
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const lines = poem.full_text.split('\n');

  return (
    <div className="space-y-6">
      <div className="mx-auto max-w-3xl px-4 py-8">
        <header className="mb-6 flex items-center gap-4">
          <Link
            href="/chinese/poetry"
            className="flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm hover:shadow-md dark:bg-slate-800"
          >
            <ChevronLeft className="h-5 w-5 text-slate-600 dark:text-slate-300" />
          </Link>
          <div className="flex items-center gap-3">
            <Feather className="h-7 w-7 text-emerald-600 dark:text-emerald-400" />
            <div>
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{poem.title}</h1>
              <p className="text-sm text-slate-500 dark:text-slate-400">{poem.poet} · {poem.dynasty}</p>
            </div>
          </div>
        </header>

        <Tabs defaultValue="appreciate">
          <TabsList className="w-full justify-start">
            <TabsTrigger value="appreciate">赏析</TabsTrigger>
            <TabsTrigger value="comprehend">理解</TabsTrigger>
            <TabsTrigger value="dictation">默写</TabsTrigger>
          </TabsList>

          <TabsContent value="appreciate">
            <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
              <div className="mb-6 text-center">
                <div className="space-y-1">
                  {lines.map((line, i) => (
                    <p
                      key={i}
                      className={cn(
                        'text-lg',
                        line.length > 10 ? 'text-xl' : 'tracking-wider'
                      )}
                      style={{ lineHeight: '2' }}
                    >
                      {line}
                    </p>
                  ))}
                </div>
              </div>

              {poem.background && (
                <div className="mt-6 rounded-xl bg-slate-50 p-4 dark:bg-slate-900">
                  <h3 className="font-medium text-slate-900 dark:text-white">创作背景</h3>
                  <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">{poem.background}</p>
                </div>
              )}

              {poem.imagery_analysis && (
                <div className="mt-4 rounded-xl bg-emerald-50 p-4 dark:bg-emerald-950">
                  <h3 className="font-medium text-emerald-900 dark:text-emerald-100">意象分析</h3>
                  <p className="mt-2 text-sm text-emerald-800 dark:text-emerald-200 whitespace-pre-wrap">
                    {poem.imagery_analysis}
                  </p>
                </div>
              )}

              {poem.artistic_techniques && (
                <div className="mt-4 rounded-xl bg-blue-50 p-4 dark:bg-blue-950">
                  <h3 className="font-medium text-blue-900 dark:text-blue-100">艺术手法</h3>
                  <p className="mt-2 text-sm text-blue-800 dark:text-blue-200 whitespace-pre-wrap">
                    {poem.artistic_techniques}
                  </p>
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="comprehend">
            <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
              <div className="mb-6 text-center">
                <div className="space-y-1">
                  {lines.map((line, i) => (
                    <p
                      key={i}
                      className="text-lg"
                      style={{ lineHeight: '2' }}
                    >
                      {line}
                    </p>
                  ))}
                </div>
              </div>

              {poem.comprehension_questions && poem.comprehension_questions.length > 0 ? (
                <div className="mt-6 space-y-4">
                  <h3 className="font-medium text-slate-900 dark:text-white">理解题目</h3>
                  {poem.comprehension_questions.map((q, i) => (
                    <div
                      key={i}
                      className="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-900"
                    >
                      <p className="text-sm text-slate-700 dark:text-slate-300">
                        {i + 1}. {q.question}
                      </p>
                      {q.hint && (
                        <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                          提示: {q.hint}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="mt-6 text-center text-slate-500 dark:text-slate-400">
                  <p>暂无理解题目</p>
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="dictation">
            <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
              <h3 className="mb-4 font-medium text-slate-900 dark:text-white">诗词默写</h3>
              <p className="mb-4 text-sm text-slate-500 dark:text-slate-400">
                请在空格中填写古诗，注意汉字的准确性
              </p>

              <div className="space-y-4">
                {lines.map((line, lineIndex) => {
                  const parts = line.split(/([\u4e00-\u9fa5])/);
                  let charIndex = 0;

                  return (
                    <div key={lineIndex} className="flex flex-wrap items-center gap-1">
                      {parts.map((part, partIndex) => {
                        if (part.length === 0) return null;
                        if (/[\u4e00-\u9fa5]/.test(part)) {
                          charIndex++;
                          return (
                            <span
                              key={partIndex}
                              className="inline-flex items-center justify-center text-center text-lg"
                              style={{ minWidth: '2em' }}
                            >
                              {part}
                            </span>
                          );
                        } else if (part.trim()) {
                          return (
                            <span
                              key={partIndex}
                              className="text-slate-400 text-lg"
                            >
                              {part}
                            </span>
                          );
                        }
                        return null;
                      })}
                    </div>
                  );
                })}
              </div>

              <div className="mt-6 flex justify-end">
                <button
                  onClick={handleDictationCheck}
                  className="flex items-center gap-2 rounded-xl bg-emerald-600 px-6 py-2 text-sm font-medium text-white transition-all hover:bg-emerald-700"
                >
                  提交默写
                </button>
              </div>

              {Object.keys(dictationResults).length > 0 && (
                <div className="mt-6 space-y-2">
                  <h4 className="font-medium text-slate-900 dark:text-white">默写结果</h4>
                  {lines.map((line, i) => (
                    <div
                      key={i}
                      className={cn(
                        'flex items-center gap-2 rounded-lg p-2',
                        dictationResults[i]
                          ? 'bg-emerald-50 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200'
                          : 'bg-red-50 text-red-800 dark:bg-red-950 dark:text-red-200'
                      )}
                    >
                      {dictationResults[i] ? (
                        <CheckCircle className="h-4 w-4" />
                      ) : (
                        <XCircle className="h-4 w-4" />
                      )}
                      <span className="text-sm">{line}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>

        <div className="mt-6 rounded-2xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
          <h3 className="mb-3 text-sm font-medium text-slate-900 dark:text-white">向AI老师提问</h3>
          <div className="space-y-3 max-h-60 overflow-y-auto">
            {chatMessages.map((msg, i) => (
              <div
                key={i}
                className={cn(
                  'rounded-lg p-3',
                  msg.role === 'user'
                    ? 'bg-blue-50 text-blue-900 dark:bg-blue-950 dark:text-blue-200 ml-8'
                    : 'bg-slate-50 text-slate-900 dark:bg-slate-900 dark:text-slate-200 mr-8'
                )}
              >
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              </div>
            ))}
          </div>
          <div className="mt-3 flex gap-2">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendChat()}
              placeholder="输入你的问题..."
              className="flex-1 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-900 dark:text-white"
            />
            <button
              onClick={handleSendChat}
              disabled={!chatInput.trim() || chatMutation.isPending}
              className={cn(
                'flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition-all',
                chatInput.trim() && !chatMutation.isPending
                  ? 'hover:bg-emerald-700'
                  : 'cursor-not-allowed opacity-50'
              )}
            >
              {chatMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}