import { test as base, expect } from '@playwright/test';

const API = 'http://localhost:8000/api/v1';

type Fixtures = {
  authenticatedPage: typeof base;
};

export const test = base.extend<Fixtures>({
  authenticatedPage: async ({ page }, use) => {
    const username = `e2e_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    const password = 'testpass1234';

    const res = await page.request.post(`${API}/auth/register`, {
      headers: { 'Content-Type': 'application/json' },
      data: JSON.stringify({ username, password }),
    });

    if (res.status() !== 201) {
      throw new Error(`Register failed (${res.status()}): ${await res.text()}`);
    }

    const { access_token } = await res.json();

    await page.goto('/');
    await page.evaluate((token) => {
      localStorage.setItem('aitutor_token', token);
    }, access_token);

    await use(page);
  },
});

export { expect };
