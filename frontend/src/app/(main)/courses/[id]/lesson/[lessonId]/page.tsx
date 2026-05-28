'use client';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { KatexRenderer } from '@/components/math/katex-renderer';
import { ChatPanel } from '@/components/chat/chat-panel';
import { ChatInput } from '@/components/chat/chat-input';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';

export default function LessonPage() {
  const params = useParams();
  const router = useRouter();
  const courseId = params.id as string;
  const lessonId = params.lessonId as string;

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-40 border-b border-gray-100 bg-white/95 backdrop-blur-sm">
        <div className="flex items-center gap-3 px-4 py-3">
          <button
            onClick={() => router.back()}
            className="flex h-9 w-9 items-center justify-center rounded-full hover:bg-gray-100"
          >
            <ArrowLeft className="h-5 w-5 text-gray-600" />
          </button>
          <h1 className="text-lg font-semibold text-gray-900">
            课程 {courseId} · 第{lessonId}课
          </h1>
        </div>
      </header>

      <div className="flex flex-1 flex-col gap-4 p-4">
        <Card className="p-5">
          <h2 className="text-lg font-semibold text-gray-900">比例与百分数</h2>
          <p className="mt-2 text-sm text-gray-600 leading-relaxed">
            比例是两个数量之间的比较关系。在这个课程中，我们将学习如何求解比例问题，
            并理解百分数在实际生活中的应用。
          </p>

          <div className="mt-4 rounded-lg bg-gray-50 p-4">
            <p className="text-sm font-medium text-gray-700">例题：</p>
            <div className="mt-2">
              <KatexRenderer latex="\\frac{3}{4} = \\frac{x}{12}" />
            </div>
          </div>
        </Card>

        <div className="flex-1">
          <ChatPanel messages={[]} className="h-64 rounded-xl border border-gray-200 bg-gray-50" />
          <div className="mt-2">
            <ChatInput onSend={(msg) => console.log(msg)} />
          </div>
        </div>

        <div className="flex gap-3">
          <Button variant="outline" className="flex-1">上一课</Button>
          <Button className="flex-1">完成课程</Button>
        </div>
      </div>
    </div>
  );
}
