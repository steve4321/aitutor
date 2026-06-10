import { test, expect } from './fixtures';

test.describe('Home page', () => {
  test('should load home page with key elements', async ({ authenticatedPage: page }) => {
    await page.goto('/home');

    await expect(page.getByText(/welcome back/i)).toBeVisible({ timeout: 10000 });
    await expect(page.getByText(/quick actions/i)).toBeVisible();

    await expect(page.getByRole('button', { name: /practice/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /KET/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /browse/i })).toBeVisible();
  });
});
