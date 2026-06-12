'use client';

import { cn } from '@/lib/utils';
import { CheckCircle2, Circle, BookOpen, Target, Loader2 } from 'lucide-react';
import type { DailyTaskItem } from '@/types/dashboard';

interface DailyTasksProps {
  tasks?: DailyTaskItem[];
  isLoading?: boolean;
  className?: string;
}

const typeIcons = {
  lesson: BookOpen,
  practice: Target,
  review: CheckCircle2,
};

export function DailyTasks({ tasks = [], isLoading = false, className }: DailyTasksProps) {
  const completedCount = tasks.filter((t) => t.completed).length;

  return (
    <div className={cn('rounded-xl border border-gray-200 bg-white p-4', className)}>
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-900">今日任务</h3>
        <span className="text-xs text-gray-500">
          {completedCount}/{tasks.length} 完成
        </span>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
        </div>
      ) : tasks.length === 0 ? (
        <div className="flex items-center justify-center py-8">
          <p className="text-sm text-gray-400">暂无待办任务，继续加油！</p>
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {tasks.map((task) => {
            const Icon = typeIcons[task.type as keyof typeof typeIcons] || BookOpen;
            return (
              <div
                key={task.id}
                className={cn(
                  'flex items-center gap-3 rounded-lg border p-3 transition-colors',
                  task.completed
                    ? 'border-green-200 bg-green-50'
                    : 'border-gray-200 bg-white hover:bg-gray-50'
                )}
              >
                <div className="shrink-0">
                  {task.completed ? (
                    <CheckCircle2 className="h-5 w-5 text-green-600" />
                  ) : (
                    <Circle className="h-5 w-5 text-gray-300" />
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <Icon className={cn('h-4 w-4', task.completed ? 'text-green-600' : 'text-gray-400')} />
                    <span
                      className={cn(
                        'text-sm font-medium truncate',
                        task.completed ? 'text-green-800 line-through' : 'text-gray-900'
                      )}
                    >
                      {task.title}
                    </span>
                  </div>
                </div>

                <span
                  className={cn(
                    'shrink-0 text-xs font-medium',
                    task.completed ? 'text-green-600' : 'text-yellow-600'
                  )}
                >
                  +{task.xp} XP
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
