import { describe, it, expect, vi } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import { renderWithProviders } from '@/test/utils';
import { LessonContent } from '../lesson/lesson-content';
import type { LessonSection } from '@/types/course';

vi.mock('../math/katex-renderer', () => ({
  KatexRenderer: ({ latex }: { latex: string }) => <span data-testid="katex">{latex}</span>,
}));

describe('LessonContent', () => {
  it('renders introduction section', () => {
    const sections: LessonSection[] = [
      { type: 'introduction', content: 'Welcome to this lesson' },
    ];
    renderWithProviders(<LessonContent sections={sections} />);
    expect(screen.getByText('开篇引言')).toBeInTheDocument();
    expect(screen.getByText('Welcome to this lesson')).toBeInTheDocument();
  });

  it('renders concept section with title and content', () => {
    const sections: LessonSection[] = [
      { type: 'concept', title: 'Pythagorean Theorem', content: 'a^2 + b^2 = c^2' },
    ];
    renderWithProviders(<LessonContent sections={sections} />);
    expect(screen.getByText('Pythagorean Theorem')).toBeInTheDocument();
    expect(screen.getByText('a^2 + b^2 = c^2')).toBeInTheDocument();
  });

  it('renders example section with problem and toggleable solution', () => {
    const sections: LessonSection[] = [
      { type: 'example', problem: 'Solve for x', solution: 'x = 5' },
    ];
    renderWithProviders(<LessonContent sections={sections} />);

    expect(screen.getByText('例题')).toBeInTheDocument();
    expect(screen.getByText('Solve for x')).toBeInTheDocument();
    expect(screen.queryByText('x = 5')).not.toBeInTheDocument();

    fireEvent.click(screen.getByText('查看解析'));
    expect(screen.getByText('x = 5')).toBeInTheDocument();

    fireEvent.click(screen.getByText('隐藏解析'));
    expect(screen.queryByText('x = 5')).not.toBeInTheDocument();
  });

  it('renders practice section and calls onAnswer when answer submitted', () => {
    const onAnswer = vi.fn();
    const sections: LessonSection[] = [
      {
        type: 'practice',
        problems: [
          { question: 'What is 2+2?', options: ['3', '4', '5', '6'], answer: 'B' },
        ],
      },
    ];

    renderWithProviders(<LessonContent sections={sections} onAnswer={onAnswer} />);

    expect(screen.getByText('课堂练习')).toBeInTheDocument();
    expect(screen.getByText('共 1 题')).toBeInTheDocument();
    expect(screen.getByText('What is 2+2?')).toBeInTheDocument();

    const optionB = screen.getByText('4').closest('button')!;
    fireEvent.click(optionB);

    const submitButton = screen.getByText('提交答案');
    fireEvent.click(submitButton);

    expect(onAnswer).toHaveBeenCalledWith(0, true, 'B', undefined);
    expect(screen.getByText('答对了！')).toBeInTheDocument();
  });

  it('calls onAnswer with false for wrong answer', () => {
    const onAnswer = vi.fn();
    const sections: LessonSection[] = [
      {
        type: 'practice',
        problems: [
          { question: 'What is 2+2?', options: ['3', '4', '5', '6'], answer: 'B' },
        ],
      },
    ];

    renderWithProviders(<LessonContent sections={sections} onAnswer={onAnswer} />);

    const optionA = screen.getByText('3').closest('button')!;
    fireEvent.click(optionA);

    const submitButton = screen.getByText('提交答案');
    fireEvent.click(submitButton);

    expect(onAnswer).toHaveBeenCalledWith(0, false, 'A', undefined);
    expect(screen.getByText(/答错了/)).toBeInTheDocument();
  });

  it('renders summary section', () => {
    const sections: LessonSection[] = [
      { type: 'summary', content: 'Key takeaways from this lesson' },
    ];
    renderWithProviders(<LessonContent sections={sections} />);
    expect(screen.getByText('本节小结')).toBeInTheDocument();
    expect(screen.getByText('Key takeaways from this lesson')).toBeInTheDocument();
  });

  it('renders multiple sections in order', () => {
    const sections: LessonSection[] = [
      { type: 'introduction', content: 'Intro text' },
      { type: 'summary', content: 'Summary text' },
    ];
    renderWithProviders(<LessonContent sections={sections} />);
    expect(screen.getByText('Intro text')).toBeInTheDocument();
    expect(screen.getByText('Summary text')).toBeInTheDocument();
  });

  it('renders latex content inside concept section', () => {
    const sections: LessonSection[] = [
      { type: 'concept', title: 'Math', content: 'The formula is $x^2$ for real numbers' },
    ];
    const { container } = renderWithProviders(<LessonContent sections={sections} />);

    const katexElements = container.querySelectorAll('.katex');
    expect(katexElements.length).toBeGreaterThanOrEqual(1);
  });
});
