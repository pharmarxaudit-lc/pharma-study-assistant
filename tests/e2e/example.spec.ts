import { test, expect } from '@playwright/test';

test.describe('Basic App Test', () => {
  test('should load the application', async ({ page }) => {
    await page.goto('/');

    // Wait for the page to load
    await page.waitForLoadState('networkidle');

    // Check that the page has loaded
    expect(page.url()).toContain('localhost:3000');
  });

  test('should have visible content', async ({ page }) => {
    await page.goto('/');

    // Wait for content to appear
    await page.waitForLoadState('domcontentloaded');

    // Check that there's some content on the page
    const body = await page.locator('body');
    await expect(body).toBeVisible();
  });
});
