import { test, expect } from '@playwright/test';

test.describe('Login flow', () => {
  test('should navigate to /login, fill form, submit, and redirect to /home', async ({ page }) => {
    await page.goto('/login');

    await expect(page.getByRole('heading', { name: /欢迎回来/i })).toBeVisible();

    await page.getByLabel('用户名').fill('testuser');
    await page.getByLabel('密码').fill('testpassword123');

    await page.getByRole('button', { name: /开始学习/i }).click();

    await expect(page).toHaveURL(/\/home/);
  });

  test('should show error message with wrong credentials', async ({ page }) => {
    await page.goto('/login');

    await page.getByLabel('用户名').fill('wronguser');
    await page.getByLabel('密码').fill('wrongpassword');

    await page.getByRole('button', { name: /开始学习/i }).click();

    await expect(page.getByText(/登录失败/i)).toBeVisible();
    await expect(page).toHaveURL(/\/login/);
  });
});
