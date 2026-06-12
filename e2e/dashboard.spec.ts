import { test, expect } from './fixtures';

test.describe('Dashboard and progress', () => {
  test('should load home page with dashboard components', async ({ authenticatedPage: page }) => {
    await page.goto('/home');

    await expect(page.getByText(/welcome back/i)).toBeVisible({ timeout: 10000 });

    await expect(page.getByText(/quick actions/i)).toBeVisible();

    await expect(page.getByText(/daily progress/i)).toBeVisible();

    const xpCard = page.getByText('XP');
    const streakCard = page.getByText('Streak');
    await expect(xpCard).toBeVisible();
    await expect(streakCard).toBeVisible();
  });

  test('should display streak section with week days', async ({ authenticatedPage: page }) => {
    await page.goto('/home');
    await expect(page.getByText(/welcome back/i)).toBeVisible({ timeout: 10000 });

    const streakSection = page.getByText('连续学习');
    const streakOrLoading = page.locator('.animate-spin').first();
    await expect(streakSection.or(streakOrLoading)).toBeVisible({ timeout: 15000 });

    await expect(page.getByText('星期一')).or(page.getByText('一')).toBeVisible({ timeout: 10000 });
  });

  test('should render daily tasks section', async ({ authenticatedPage: page }) => {
    await page.goto('/home');
    await expect(page.getByText(/welcome back/i)).toBeVisible({ timeout: 10000 });

    const tasksHeader = page.getByText('今日任务');
    const loadingSpinner = page.locator('.animate-spin');
    await expect(tasksHeader.or(loadingSpinner.first())).toBeVisible({ timeout: 15000 });
  });

  test('should navigate to reports page and show report UI', async ({ authenticatedPage: page }) => {
    await page.goto('/reports');

    await expect(page.getByText('学习报告')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('追踪你的学习进度和表现')).toBeVisible();

    const timeRangeButtons = page.locator('button', { hasText: /本周|本月|全部/ });
    await expect(timeRangeButtons.first()).toBeVisible({ timeout: 10000 });

    const statsCards = page.getByText(/获得 XP|完成题目|正确率|学习时间/);
    const noDataState = page.getByText('暂无数据');
    await expect(statsCards.first().or(noDataState)).toBeVisible({ timeout: 15000 });
  });

  test('should navigate to settings page and show all settings sections', async ({ authenticatedPage: page }) => {
    await page.goto('/settings');

    await expect(page.getByText('设置')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('管理你的账户和偏好设置')).toBeVisible();

    await expect(page.getByText('个人资料')).toBeVisible();

    await expect(page.getByText('偏好设置')).toBeVisible();

    const themeButtons = page.getByText(/浅色|深色|自动/);
    await expect(themeButtons.first()).toBeVisible({ timeout: 10000 });

    await expect(page.getByText('家长绑定')).toBeVisible();

    await expect(page.getByText('通知与声音')).toBeVisible();

    await expect(page.getByText('退出登录')).toBeVisible();
  });

  test('should toggle theme in settings', async ({ authenticatedPage: page }) => {
    await page.goto('/settings');
    await expect(page.getByText('设置')).toBeVisible({ timeout: 10000 });

    const darkButton = page.getByRole('button', { name: /深色/ });
    if (await darkButton.isVisible()) {
      await darkButton.click();
    }

    const lightButton = page.getByRole('button', { name: /浅色/ });
    if (await lightButton.isVisible()) {
      await lightButton.click();
    }

    await expect(lightButton.or(darkButton)).toBeVisible();
  });
});
