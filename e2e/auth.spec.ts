import { test, expect } from '@playwright/test';

const API = process.env.E2E_API_URL || 'http://localhost:8000/api/v1';

test.describe('Login flow', () => {
  test('should navigate to /login, fill form, submit, and redirect to /home', async ({ page }) => {
    const username = `login_${Date.now()}`;
    const reg = await page.request.post(`${API}/auth/register`, {
      headers: { 'Content-Type': 'application/json' },
      data: JSON.stringify({ username, password: 'testpassword123' }),
    });
    expect(reg.status()).toBe(201);

    await page.goto('/login');
    await expect(page.getByRole('heading', { name: /welcome back/i })).toBeVisible();

    await page.locator('#username').fill(username);
    await page.locator('#password').fill('testpassword123');
    await page.getByRole('button', { name: /sign in/i }).click();

    await expect(page).toHaveURL(/\/home/, { timeout: 10000 });
  });

  test('should show error message with wrong credentials', async ({ page }) => {
    await page.goto('/login');

    await page.locator('#username').fill('nonexistent_user_xyz');
    await page.locator('#password').fill('wrongpassword');
    await page.getByRole('button', { name: /sign in/i }).click();

    await expect(page.getByText(/authentication|invalid|failed|error|unauthorized/i)).toBeVisible({ timeout: 10000 });
    await expect(page).toHaveURL(/\/login/);
  });
});
