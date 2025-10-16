import { test, expect } from '@playwright/test';

test.describe('Question Review', () => {
  test('should navigate to question review from history', async ({ page }) => {
    // Navigate to the app
    await page.goto('http://localhost:5001');

    // Wait for app to load
    await page.waitForLoadState('networkidle');

    // Go to history page
    await page.click('text=History');
    await page.waitForURL(/.*#\/history/);

    // Check if we have any sessions
    const hasHistory = await page.locator('.session-card').count() > 0;

    if (!hasHistory) {
      console.log('No session history available - skipping review test');
      return;
    }

    // Click "Review Answers" button on first session
    await page.locator('.session-card').first().locator('.review-button').click();

    // Wait for navigation to review page
    await page.waitForURL(/.*#\/review\/\d+/);

    // Verify we're on the review page
    await expect(page.locator('h1')).toContainText('Question Review');

    // Take screenshot
    await page.screenshot({ path: 'test-results/question-review.png', fullPage: true });

    console.log('Question review page loaded successfully');
  });

  test('should display session summary', async ({ page }) => {
    await page.goto('http://localhost:5001/#/history');
    await page.waitForLoadState('networkidle');

    const hasHistory = await page.locator('.session-card').count() > 0;
    if (!hasHistory) {
      console.log('No session history - skipping summary test');
      return;
    }

    // Go to review page
    await page.locator('.session-card').first().locator('.review-button').click();
    await page.waitForURL(/.*#\/review\/\d+/);

    // Check for summary elements
    await expect(page.locator('.session-summary')).toBeVisible();
    await expect(page.locator('.stat-label')).toHaveCount(4); // Score, Percentage, Duration, Status

    console.log('Session summary displayed correctly');
  });

  test('should display question list with correct/incorrect highlighting', async ({ page }) => {
    await page.goto('http://localhost:5001/#/history');
    await page.waitForLoadState('networkidle');

    const hasHistory = await page.locator('.session-card').count() > 0;
    if (!hasHistory) {
      console.log('No session history - skipping question list test');
      return;
    }

    // Go to review page
    await page.locator('.session-card').first().locator('.review-button').click();
    await page.waitForURL(/.*#\/review\/\d+/);

    // Check for questions
    const questionCount = await page.locator('.question-card').count();
    expect(questionCount).toBeGreaterThan(0);

    // Check first question has proper structure
    const firstQuestion = page.locator('.question-card').first();
    await expect(firstQuestion.locator('.question-text')).toBeVisible();
    await expect(firstQuestion.locator('.option-item')).toHaveCount(4); // Assuming 4 options
    await expect(firstQuestion.locator('.explanation-box')).toBeVisible();

    console.log(`Found ${questionCount} questions with proper structure`);
  });

  test('should filter questions by correct/incorrect', async ({ page }) => {
    await page.goto('http://localhost:5001/#/history');
    await page.waitForLoadState('networkidle');

    const hasHistory = await page.locator('.session-card').count() > 0;
    if (!hasHistory) {
      console.log('No session history - skipping filter test');
      return;
    }

    // Go to review page
    await page.locator('.session-card').first().locator('.review-button').click();
    await page.waitForURL(/.*#\/review\/\d+/);

    // Get total questions count
    const totalQuestions = await page.locator('.question-card').count();

    // Click "Correct" filter
    await page.click('text=Correct');
    await page.waitForTimeout(500); // Wait for filter to apply

    const correctCount = await page.locator('.question-card').count();
    console.log(`Total: ${totalQuestions}, After filtering correct: ${correctCount}`);

    // Click "Incorrect" filter
    await page.click('text=Incorrect');
    await page.waitForTimeout(500);

    const incorrectCount = await page.locator('.question-card').count();
    console.log(`After filtering incorrect: ${incorrectCount}`);

    // Verify counts make sense
    expect(correctCount + incorrectCount).toBeLessThanOrEqual(totalQuestions);

    console.log('Filters working correctly');
  });

  test('should display correct answer markers', async ({ page }) => {
    await page.goto('http://localhost:5001/#/history');
    await page.waitForLoadState('networkidle');

    const hasHistory = await page.locator('.session-card').count() > 0;
    if (!hasHistory) {
      console.log('No session history - skipping markers test');
      return;
    }

    // Go to review page
    await page.locator('.session-card').first().locator('.review-button').click();
    await page.waitForURL(/.*#\/review\/\d+/);

    // Look for answer markers
    const correctMarkers = page.locator('.correct-marker');
    const hasCorrectMarkers = await correctMarkers.count() > 0;

    if (hasCorrectMarkers) {
      await expect(correctMarkers.first()).toContainText('Correct Answer');
      console.log('Correct answer markers displayed');
    }

    // Check for wrong answer markers (if any incorrect answers)
    const wrongMarkers = page.locator('.wrong-marker');
    const hasWrongMarkers = await wrongMarkers.count() > 0;

    if (hasWrongMarkers) {
      await expect(wrongMarkers.first()).toContainText('Your Answer');
      console.log('Wrong answer markers displayed');
    }
  });

  test('should navigate back to history', async ({ page }) => {
    await page.goto('http://localhost:5001/#/history');
    await page.waitForLoadState('networkidle');

    const hasHistory = await page.locator('.session-card').count() > 0;
    if (!hasHistory) {
      console.log('No session history - skipping navigation test');
      return;
    }

    // Go to review page
    await page.locator('.session-card').first().locator('.review-button').click();
    await page.waitForURL(/.*#\/review\/\d+/);

    // Click back button
    await page.click('text=Back to History');

    // Verify we're back on history page
    await page.waitForURL(/.*#\/history/);
    await expect(page.locator('h1')).toContainText('Exam History');

    console.log('Navigation back to history works');
  });
});
