import { test, expect } from '@playwright/test';

test.describe('Console Error Check', () => {
  test('should check for console errors on Exam Prep page', async ({ page }) => {
    const consoleMessages: Array<{ type: string; text: string }> = [];

    // Listen for all console messages
    page.on('console', (msg) => {
      consoleMessages.push({
        type: msg.type(),
        text: msg.text(),
      });
    });

    // Listen for page errors
    const pageErrors: string[] = [];
    page.on('pageerror', (error) => {
      pageErrors.push(error.message);
    });

    // Navigate to localhost:5001
    await page.goto('http://localhost:5001', { waitUntil: 'networkidle' });

    // Click on "Exam Prep" link/button
    await page.click('text=Exam Prep');

    // Wait a bit for any async operations
    await page.waitForTimeout(2000);

    // Filter console errors and warnings
    const errors = consoleMessages.filter((msg) => msg.type === 'error');
    const warnings = consoleMessages.filter((msg) => msg.type === 'warning');

    // Log all console messages for debugging
    console.log('\n=== Console Messages ===');
    console.log('Errors:', errors.length);
    errors.forEach((err) => console.log('  ERROR:', err.text));

    console.log('\nWarnings:', warnings.length);
    warnings.forEach((warn) => console.log('  WARNING:', warn.text));

    console.log('\nPage Errors:', pageErrors.length);
    pageErrors.forEach((err) => console.log('  PAGE ERROR:', err));

    // Take a screenshot for verification
    await page.screenshot({ path: 'test-results/exam-prep-page.png', fullPage: true });

    // Report findings
    if (errors.length > 0 || pageErrors.length > 0) {
      console.log('\n⚠️  Console errors detected!');
    } else {
      console.log('\n✓ No console errors found');
    }

    // Optional: Fail the test if there are errors (comment out if you just want to check)
    // expect(errors.length).toBe(0);
    // expect(pageErrors.length).toBe(0);
  });
});
