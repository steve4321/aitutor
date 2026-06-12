import { test, expect } from './fixtures';

test.describe('KET English flow', () => {
  test('should navigate to KET hub and show four skill cards', async ({ authenticatedPage: page }) => {
    await page.goto('/ket');

    await expect(page.getByText('KET 英语')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('Cambridge A2 Key')).toBeVisible();

    await expect(page.getByText('阅读')).toBeVisible();
    await expect(page.getByText('写作')).toBeVisible();
    await expect(page.getByText('听力')).toBeVisible();
    await expect(page.getByText('口语')).toBeVisible();

    const skillLinks = page.locator('a[href^="/ket/"]');
    await expect(skillLinks).toHaveCount(4);
  });

  test('should navigate to KET reading — show questions or empty state', async ({ authenticatedPage: page }) => {
    await page.goto('/ket/reading');

    await expect(page.getByText('阅读理解')).toBeVisible({ timeout: 10000 });

    const questionContent = page.locator('.rounded-2xl.border');
    const emptyState = page.getByText('暂无题目');
    await expect(questionContent.first().or(emptyState)).toBeVisible({ timeout: 15000 });
  });

  test('should navigate to KET writing — show writing editor or empty state', async ({ authenticatedPage: page }) => {
    await page.goto('/ket/writing');

    await expect(page.getByText('写作练习')).toBeVisible({ timeout: 10000 });

    const taskList = page.getByText('选择写作任务');
    const emptyState = page.getByText('暂无题目');
    await expect(taskList.or(emptyState)).toBeVisible({ timeout: 15000 });
  });

  test('should navigate to KET listening — show listening page or empty state', async ({ authenticatedPage: page }) => {
    await page.goto('/ket/listening');

    await expect(page.getByText('听力练习')).toBeVisible({ timeout: 10000 });

    const questionContent = page.locator('.rounded-2xl.border');
    const emptyState = page.getByText('暂无题目');
    await expect(questionContent.first().or(emptyState)).toBeVisible({ timeout: 15000 });
  });

  test('should navigate to KET speaking — show speaking tasks or empty state', async ({ authenticatedPage: page }) => {
    await page.goto('/ket/speaking');

    await expect(page.getByText('口语练习')).toBeVisible({ timeout: 10000 });

    const taskList = page.getByText('选择口语任务');
    const emptyState = page.getByText('暂无题目');
    await expect(taskList.or(emptyState)).toBeVisible({ timeout: 15000 });
  });

  test('should navigate back to KET hub via back button from reading', async ({ authenticatedPage: page }) => {
    await page.goto('/ket/reading');
    await expect(page.getByText('阅读理解')).toBeVisible({ timeout: 10000 });

    await page.click('a[href="/ket"]');
    await expect(page).toHaveURL(/\/ket$/, { timeout: 10000 });
    await expect(page.getByText('KET 英语')).toBeVisible();
  });
});
