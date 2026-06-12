import { test, expect } from './fixtures';

test.describe('Chinese module flow', () => {
  test('should navigate to Chinese hub and show composition and poetry sections', async ({ authenticatedPage: page }) => {
    await page.goto('/chinese');

    await expect(page.getByText('语文')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('小学4-6年级语文素养训练')).toBeVisible();

    await expect(page.getByText('作文')).toBeVisible();
    await expect(page.getByText('古诗词')).toBeVisible();

    const moduleLinks = page.locator('a[href^="/chinese/"]');
    await expect(moduleLinks).toHaveCount(2);
  });

  test('should navigate to composition — show writing tasks or empty state', async ({ authenticatedPage: page }) => {
    await page.goto('/chinese/composition');

    await expect(page.getByText('作文练习')).toBeVisible({ timeout: 10000 });

    const taskCards = page.locator('a[href^="/chinese/composition/"]');
    const emptyState = page.getByText('暂无题目');
    await expect(taskCards.first().or(emptyState)).toBeVisible({ timeout: 15000 });
  });

  test('should navigate to poetry list — show poems or empty state', async ({ authenticatedPage: page }) => {
    await page.goto('/chinese/poetry');

    await expect(page.getByText('古诗词')).toBeVisible({ timeout: 10000 });

    const poemCards = page.locator('a[href^="/chinese/poetry/"]');
    const emptyState = page.getByText('暂无诗词');
    await expect(poemCards.first().or(emptyState)).toBeVisible({ timeout: 15000 });
  });

  test('should show poem detail page with tabs when clicking a poem', async ({ authenticatedPage: page }) => {
    await page.goto('/chinese/poetry');
    await expect(page.getByText('古诗词')).toBeVisible({ timeout: 10000 });

    const poemCards = page.locator('a[href^="/chinese/poetry/"]');
    const emptyState = page.getByText('暂无诗词');

    const hasPoems = await poemCards.first().isVisible({ timeout: 5000 }).catch(() => false);

    if (!hasPoems) {
      await expect(emptyState).toBeVisible();
      return;
    }

    await poemCards.first().click();

    await expect(page).toHaveURL(/\/chinese\/poetry\/[a-f0-9-]+/, { timeout: 10000 });

    await expect(page.getByText('诗词赏析')).toBeVisible({ timeout: 10000 });

    await expect(page.getByRole('tab', { name: '赏析' })).toBeVisible();
    await expect(page.getByRole('tab', { name: '理解' })).toBeVisible();
    await expect(page.getByRole('tab', { name: '默写' })).toBeVisible();
  });

  test('should navigate back to Chinese hub via back button from composition', async ({ authenticatedPage: page }) => {
    await page.goto('/chinese/composition');
    await expect(page.getByText('作文练习')).toBeVisible({ timeout: 10000 });

    await page.click('a[href="/chinese"]');
    await expect(page).toHaveURL(/\/chinese$/, { timeout: 10000 });
    await expect(page.getByText('语文')).toBeVisible();
  });
});
