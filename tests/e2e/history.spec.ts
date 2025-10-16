import { test, expect } from '@playwright/test';

test.describe('History View', () => {
  test('should load history page', async ({ page }) => {
    // Navigate to the app
    await page.goto('http://localhost:5001');

    // Wait for app to load
    await page.waitForLoadState('networkidle');

    // Click History link in navigation
    await page.click('text=History');

    // Wait for navigation
    await page.waitForURL(/.*#\/history/);

    // Check that we're on the history page
    await expect(page.locator('h1')).toContainText('Exam History');

    // Take screenshot
    await page.screenshot({ path: 'test-results/history-view.png', fullPage: true });

    console.log('History page loaded successfully');
  });

  test('should show empty state or sessions', async ({ page }) => {
    await page.goto('http://localhost:5001/#/history');
    await page.waitForLoadState('networkidle');

    // Should show either empty state or sessions list
    const emptyState = page.locator('.empty-state');
    const sessionsList = page.locator('.sessions-list');

    const hasEmptyState = await emptyState.isVisible().catch(() => false);
    const hasSessionsList = await sessionsList.isVisible().catch(() => false);

    expect(hasEmptyState || hasSessionsList).toBeTruthy();

    if (hasEmptyState) {
      console.log('Empty state displayed (no sessions yet)');
      await expect(emptyState).toContainText('No History Yet');
    } else {
      console.log('Sessions list displayed');
      const sessions = await page.locator('.session-card').count();
      console.log(`Found ${sessions} sessions`);
    }

    await page.screenshot({ path: 'test-results/history-state.png', fullPage: true });
  });
});
