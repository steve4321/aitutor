import { test, expect } from '@playwright/test';

test.describe('Course listing', () => {
  test('should display course cards on /courses page', async ({ page }) => {
    await page.goto('/courses');

    await expect(page.getByRole('heading', { name: /全部课程/ })).toBeVisible();
    await expect(page.getByPlaceholder('搜索课程...')).toBeVisible();

    await expect(page.getByRole('button', { name: /全部/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /AMC/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /KET/i })).toBeVisible();

    const courseCards = page.locator('.bg-\\[var\(--color-surface\)\\]');
    const emptyState = page.getByText(/还没有课程/i);

    await expect(courseCards.or(emptyState)).toBeVisible({ timeout: 15000 });
  });
});
