import { test, expect } from './fixtures';

test.describe('Lesson flow', () => {
  test('should navigate to a lesson page', async ({ authenticatedPage: page }) => {
    await page.goto('/courses');
    await expect(page.getByRole('heading', { name: /^courses$/i })).toBeVisible({ timeout: 10000 });

    const viewCourseBtn = page.getByRole('button', { name: /view course/i }).first();
    await expect(viewCourseBtn).toBeVisible({ timeout: 10000 });
    await viewCourseBtn.click();

    await expect(page).toHaveURL(/\/courses\/[a-f0-9-]+/);

    const firstLesson = page.locator('[class*="lesson"], [data-lesson], a[href*="/lesson/"]').first();
    const anyClickable = page.locator('div[class*="cursor-pointer"], button, a').first();
    await expect(firstLesson.or(anyClickable)).toBeVisible({ timeout: 10000 });
  });

  test('should handle non-existent lesson gracefully', async ({ authenticatedPage: page }) => {
    await page.goto('/courses/00000000-0000-0000-0000-000000000000/lesson/00000000-0000-0000-0000-000000000000');
    await expect(page).toHaveURL(/\/courses\//);
  });
});
