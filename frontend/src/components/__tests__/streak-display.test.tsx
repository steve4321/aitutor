import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithProviders } from '@/test/utils';
import { StreakDisplay } from '../dashboard/streak-display';

describe('StreakDisplay', () => {
  it('renders current streak count', () => {
    renderWithProviders(<StreakDisplay currentStreak={5} longestStreak={10} />);
    expect(screen.getByText('5')).toBeInTheDocument();
  });

  it('renders longest streak count', () => {
    renderWithProviders(<StreakDisplay currentStreak={3} longestStreak={12} />);
    expect(screen.getByText('12')).toBeInTheDocument();
  });

  it('shows fire icon via Flame component', () => {
    const { container } = renderWithProviders(
      <StreakDisplay currentStreak={7} longestStreak={7} />,
    );
    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });

  it('shows streak flame as active when streak > 0', () => {
    const { container } = renderWithProviders(
      <StreakDisplay currentStreak={5} longestStreak={10} />,
    );
    const flameContainer = container.querySelector('.animate-pulse');
    expect(flameContainer).toBeInTheDocument();
  });

  it('shows streak flame as inactive when streak is 0', () => {
    const { container } = renderWithProviders(
      <StreakDisplay currentStreak={0} longestStreak={5} />,
    );
    const flameContainer = container.querySelector('.animate-pulse');
    expect(flameContainer).not.toBeInTheDocument();
  });

  it('handles zero streak', () => {
    renderWithProviders(<StreakDisplay currentStreak={0} longestStreak={0} />);
    const streakNumbers = screen.getAllByText('0');
    expect(streakNumbers.length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText('开始你的连续学习之旅吧！')).toBeInTheDocument();
  });

  it('shows encouraging message for streak >= 3', () => {
    renderWithProviders(<StreakDisplay currentStreak={3} longestStreak={5} />);
    expect(screen.getByText('继续保持！')).toBeInTheDocument();
  });

  it('shows celebration message for streak >= 7', () => {
    renderWithProviders(<StreakDisplay currentStreak={7} longestStreak={7} />);
    expect(screen.getByText('太棒了！已连续学习一周！')).toBeInTheDocument();
  });

  it('renders week day labels', () => {
    renderWithProviders(<StreakDisplay currentStreak={1} longestStreak={1} />);
    expect(screen.getByText('一')).toBeInTheDocument();
    expect(screen.getByText('二')).toBeInTheDocument();
    expect(screen.getByText('三')).toBeInTheDocument();
    expect(screen.getByText('四')).toBeInTheDocument();
    expect(screen.getByText('五')).toBeInTheDocument();
    expect(screen.getByText('六')).toBeInTheDocument();
    expect(screen.getByText('日')).toBeInTheDocument();
  });

  it('renders active days with checkmark and inactive with X', () => {
    const { container } = renderWithProviders(
      <StreakDisplay
        currentStreak={1}
        longestStreak={1}
        weekData={[true, false, true, false, true, false, true]}
      />,
    );

    const checks = container.querySelectorAll('.lucide-check');
    const crosses = container.querySelectorAll('.lucide-x');
    expect(checks.length).toBe(4);
    expect(crosses.length).toBe(3);
  });

  it('renders default weekData when not provided', () => {
    const { container } = renderWithProviders(<StreakDisplay currentStreak={5} longestStreak={10} />);
    const checks = container.querySelectorAll('.lucide-check');
    const crosses = container.querySelectorAll('.lucide-x');
    expect(checks.length).toBe(0);
    expect(crosses.length).toBe(7);
  });

  it('renders day unit text', () => {
    renderWithProviders(<StreakDisplay currentStreak={5} longestStreak={10} />);
    const dayLabels = screen.getAllByText('天');
    expect(dayLabels.length).toBe(2);
  });

  it('renders section labels', () => {
    renderWithProviders(<StreakDisplay currentStreak={5} longestStreak={10} />);
    expect(screen.getByText('连续学习')).toBeInTheDocument();
    expect(screen.getByText('最长连续')).toBeInTheDocument();
  });
});
