import { test, expect, request } from '@playwright/test';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

test.describe('Enroll API', () => {
  test('enroll endpoint is reachable and creates an enrollment', async () => {
    const ctx = await request.newContext({ baseURL: API_BASE });

    const username = `enroll${Date.now()}`;
    const reg = await ctx.post('/auth/register', {
      data: { username, password: 'testpass1234' },
    });
    expect(reg.status()).toBe(201);
    const { access_token } = await reg.json();

    const coursesRes = await ctx.get('/courses', {
      headers: { Authorization: `Bearer ${access_token}` },
    });
    expect(coursesRes.status()).toBe(200);
    const courses = await coursesRes.json();
    expect(courses.length).toBeGreaterThan(0);
    const firstCourseId = courses[0].id;

    const enrollRes = await ctx.post(`/courses/${firstCourseId}/enroll`, {
      headers: { Authorization: `Bearer ${access_token}` },
    });
    expect(enrollRes.status()).toBe(201);
    const enrollBody = await enrollRes.json();
    expect(enrollBody.message).toMatch(/Enrolled|Already/);

    const enrollAgain = await ctx.post(`/courses/${firstCourseId}/enroll`, {
      headers: { Authorization: `Bearer ${access_token}` },
    });
    expect(enrollAgain.status()).toBe(201);
    const again = await enrollAgain.json();
    expect(again.message).toBe('Already enrolled');
  });

  test('enroll on nonexistent course returns 404', async () => {
    const ctx = await request.newContext({ baseURL: API_BASE });

    const username = `en404${Date.now()}`;
    const reg = await ctx.post('/auth/register', {
      data: { username, password: 'testpass1234' },
    });
    const { access_token } = await reg.json();

    const res = await ctx.post('/courses/00000000-0000-0000-0000-000000000000/enroll', {
      headers: { Authorization: `Bearer ${access_token}` },
    });
    expect(res.status()).toBe(404);
  });
});
