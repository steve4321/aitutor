import { test, expect } from '@playwright/test';

test.describe('Home page', () => {
  test('should load home page with key elements', async ({ page }) => {
    await page.goto('/home');

    await expect(page.getByRole('heading', { name: /欢迎回来/i })).toBeVisible();
    await expect(page.getByText(/今天的学习计划/i)).toBeVisible();
    await expect(page.getByText(/快捷操作/i)).toBeVisible();

    await expect(page.getByRole('button', { name: /练习/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /KET/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /浏览课程/i })).toBeVisible();

    await expect(page.getByText(/今日目标/i)).toBeVisible();
  });
});
