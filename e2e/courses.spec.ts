import { test, expect } from './fixtures';

test.describe('Course listing', () => {
  test('should display course cards on /courses page', async ({ authenticatedPage: page }) => {
    await page.goto('/courses');

    await expect(page.getByRole('heading', { name: /^courses$/i })).toBeVisible({ timeout: 10000 });

    await expect(page.getByRole('button', { name: /all/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /AMC/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /KET/i })).toBeVisible();

    const viewCourseButtons = page.getByRole('button', { name: /view course/i });
    const emptyState = page.getByText(/no courses found/i);

    await expect(viewCourseButtons.first().or(emptyState)).toBeVisible({ timeout: 15000 });
  });
});
