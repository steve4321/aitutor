import { test, expect, request } from '@playwright/test';

const API = 'http://localhost:8000/api/v1';

test.describe('Enroll API', () => {
  test('enroll endpoint is reachable and creates an enrollment', async () => {
    const ctx = await request.newContext();

    const username = `enroll${Date.now()}_${Math.random().toString(36).slice(2, 6)}`;
    const reg = await ctx.post(`${API}/auth/register`, {
      headers: { 'Content-Type': 'application/json' },
      data: JSON.stringify({ username, password: 'testpass1234' }),
    });
    expect(reg.status(), `Register failed: ${await reg.text()}`).toBe(201);
    const { access_token } = await reg.json();

    const coursesRes = await ctx.get(`${API}/courses`, {
      headers: { Authorization: `Bearer ${access_token}` },
    });
    expect(coursesRes.status()).toBe(200);
    const courses = await coursesRes.json();
    expect(courses.length).toBeGreaterThan(0);
    const firstCourseId = courses[0].id;

    const enrollRes = await ctx.post(`${API}/courses/${firstCourseId}/enroll`, {
      headers: { Authorization: `Bearer ${access_token}` },
    });
    expect(enrollRes.status()).toBe(201);
    const enrollBody = await enrollRes.json();
    expect(enrollBody.message).toMatch(/Enrolled|Already/);

    const enrollAgain = await ctx.post(`${API}/courses/${firstCourseId}/enroll`, {
      headers: { Authorization: `Bearer ${access_token}` },
    });
    expect(enrollAgain.status()).toBe(201);
    const again = await enrollAgain.json();
    expect(again.message).toBe('Already enrolled');
  });

  test('enroll on nonexistent course returns 404', async () => {
    const ctx = await request.newContext();

    const username = `en404${Date.now()}_${Math.random().toString(36).slice(2, 6)}`;
    const reg = await ctx.post(`${API}/auth/register`, {
      headers: { 'Content-Type': 'application/json' },
      data: JSON.stringify({ username, password: 'testpass1234' }),
    });
    expect(reg.status(), `Register failed: ${await reg.text()}`).toBe(201);
    const { access_token } = await reg.json();

    const res = await ctx.post(`${API}/courses/00000000-0000-0000-0000-000000000000/enroll`, {
      headers: { Authorization: `Bearer ${access_token}` },
    });
    expect(res.status()).toBe(404);
  });
});
