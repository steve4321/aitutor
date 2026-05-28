'use client';

import { cn } from '@/lib/utils';
import { CheckCircle2, Circle, BookOpen, Target } from 'lucide-react';

interface DailyTask {
  id: string;
  title: string;
  type: 'lesson' | 'practice' | 'review';
  xp: number;
  completed: boolean;
}

interface DailyTasksProps {
  tasks?: DailyTask[];
  className?: string;
}

const defaultTasks: DailyTask[] = [
  { id: '1', title: '完成今日数学课程', type: 'lesson', xp: 50, completed: false },
  { id: '2', title: '练习10道代数题', type: 'practice', xp: 30, completed: false },
  { id: '3', title: 'KET阅读训练', type: 'lesson', xp: 40, completed: true },
  { id: '4', title: '复习错题集', type: 'review', xp: 20, completed: false },
];

const typeIcons = {
  lesson: BookOpen,
  practice: Target,
  review: CheckCircle2,
};

export function DailyTasks({ tasks = defaultTasks, className }: DailyTasksProps) {
  const completedCount = tasks.filter((t) => t.completed).length;

  return (
    <div className={cn('rounded-xl border border-gray-200 bg-white p-4', className)}>
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-900">今日任务</h3>
        <span className="text-xs text-gray-500">
          {completedCount}/{tasks.length} 完成
        </span>
      </div>

      <div className="flex flex-col gap-2">
        {tasks.map((task) => {
          const Icon = typeIcons[task.type];
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
    </div>
  );
}
