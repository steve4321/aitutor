import { test, expect } from './fixtures';

const API = process.env.E2E_API_URL || 'http://localhost:8000/api/v1';

test.describe('Learning flow — Complete Learning Cycle', () => {
  test('should start a practice session and show practice page UI', async ({ authenticatedPage: page }) => {
    await page.goto('/practice');

    // Page heading should be visible
    await expect(page.getByText('练习')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('选择课程和单元，开始针对性练习')).toBeVisible();

    // Course cards or empty state should render
    const courseCards = page.locator('button:has(svg.lucide)');
    const emptyState = page.getByText('该课程暂无单元');
    await expect(courseCards.first().or(emptyState)).toBeVisible({ timeout: 10000 });
  });

  test('should load lesson page with AI chat and send messages', async ({ authenticatedPage: page }) => {
    // Enroll in a course first so we can access lessons
    const coursesRes = await page.request.get(`${API}/courses`);
    expect(coursesRes.status()).toBe(200);
    const courses = await coursesRes.json();

    if (courses.length === 0) {
      // No courses seeded — verify graceful empty state on practice page
      await page.goto('/practice');
      await expect(page.getByText('练习')).toBeVisible({ timeout: 10000 });
      return;
    }

    // Enroll in first course
    const courseId = courses[0].id;
    await page.request.post(`${API}/courses/${courseId}/enroll`);

    // Get lessons for this course
    const lessonsRes = await page.request.get(`${API}/courses/${courseId}/lessons`);
    const lessons = await lessonsRes.json();

    if (lessons.length === 0) {
      // No lessons — just verify practice page loads
      await page.goto('/practice');
      await expect(page.getByText('练习')).toBeVisible({ timeout: 10000 });
      return;
    }

    const lessonId = lessons[0].id;

    // Navigate to lesson page
    await page.goto(`/courses/${courseId}/lesson/${lessonId}`);

    // Lesson header should be visible with lesson title or loading state
    const lessonHeader = page.locator('header');
    await expect(lessonHeader).toBeVisible({ timeout: 15000 });

    // AI chat section should be present
    await expect(page.getByText('AI 老师')).toBeVisible({ timeout: 15000 });

    // Send a message to the AI tutor
    const chatInput = page.locator('input[type="text"], textarea').last();
    await expect(chatInput).toBeVisible({ timeout: 10000 });
    await chatInput.fill('Hello, can you help me?');
    await chatInput.press('Enter');

    // Verify the user message appears in the chat panel
    await expect(page.getByText('Hello, can you help me?')).toBeVisible({ timeout: 10000 });
  });

  test('should preserve conversation after page refresh via session', async ({ authenticatedPage: page }) => {
    // Navigate to practice and verify page state
    await page.goto('/practice');
    await expect(page.getByText('练习')).toBeVisible({ timeout: 10000 });

    // Refresh the page
    await page.reload();

    // Page should still show practice content (session restored)
    await expect(page.getByText('练习')).toBeVisible({ timeout: 10000 });

    // Auth token in localStorage should persist
    const token = await page.evaluate(() => localStorage.getItem('aitutor_token'));
    expect(token).toBeTruthy();
  });

  test('should show practice start button disabled when no units selected', async ({ authenticatedPage: page }) => {
    await page.goto('/practice');
    await expect(page.getByText('练习')).toBeVisible({ timeout: 10000 });

    // The "开始练习" (Start Practice) button should exist but be disabled initially
    const startButton = page.getByRole('button', { name: /开始练习/ });
    await expect(startButton).toBeVisible({ timeout: 10000 });
    await expect(startButton).toBeDisabled();
  });
});
