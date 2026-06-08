import { test, expect } from '@playwright/test';

test.describe('Lesson flow', () => {
  test('should navigate to a lesson and see content sections', async ({ page }) => {
    const username = `lesson${Date.now()}`;
    await page.goto('/register');
    await page.getByLabel('用户名').fill(username);
    await page.getByLabel('密码').fill('testpass1234');
    await page.getByRole('button', { name: /注册|开始/i }).click();
    await expect(page).toHaveURL(/\/home/);

    await page.goto('/courses');
    await expect(page.getByRole('heading', { name: /全部课程/ })).toBeVisible();
    const firstCourse = page.locator('a[href^="/courses/"]').first();
    await firstCourse.click();

    await expect(page).toHaveURL(/\/courses\/[a-f0-9-]+$/);
    const firstLesson = page.locator('text=min').first();
    await firstLesson.click();

    await expect(page).toHaveURL(/\/lessons\/[a-f0-9-]+$/);
    await expect(page.getByRole('heading', { name: /学习目标/ })).toBeVisible({ timeout: 10000 });
  });

  test('should show validation error on /lessons/{id} with bad UUID', async ({ page }) => {
    const username = `lvp${Date.now()}`;
    await page.goto('/register');
    await page.getByLabel('用户名').fill(username);
    await page.getByLabel('密码').fill('testpass1234');
    await page.getByRole('button', { name: /注册|开始/i }).click();
    await expect(page).toHaveURL(/\/home/);

    const response = await page.goto('/courses/00000000-0000-0000-0000-000000000000/lesson/00000000-0000-0000-0000-000000000000');
    expect(response?.status()).toBe(404);
  });
});
