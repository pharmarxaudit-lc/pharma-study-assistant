const { chromium } = require('playwright');

(async () => {
  console.log('Starting console log test...\n');

  const browser = await chromium.launch({
    headless: false,
    slowMo: 500
  });

  const page = await browser.newPage();

  // Capture console logs
  page.on('console', msg => {
    console.log(`[BROWSER ${msg.type()}]:`, msg.text());
  });

  // Capture errors
  page.on('pageerror', error => {
    console.error('[BROWSER ERROR]:', error.message);
  });

  try {
    console.log('1. Navigating to app with hard refresh...');
    await page.goto('http://localhost:5001', { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);

    console.log('\n2. Navigating to exam config...');
    await page.goto('http://localhost:5001/#/exam', { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);

    console.log('\n3. Selecting 10 questions...');
    const button10 = await page.locator('button:has-text("10")').first();
    await button10.click();
    await page.waitForTimeout(500);

    console.log('\n4. Clicking Start Session...');
    const startButton = await page.locator('button:has-text("Start Session")');
    await startButton.click();
    await page.waitForTimeout(3000);

    console.log('\n5. Checking for error or success...');
    const errorMessage = await page.locator('.error-message').count();
    if (errorMessage > 0) {
      const errorText = await page.locator('.error-message').textContent();
      console.log('ERROR:', errorText);
      await page.screenshot({ path: '/tmp/console_error.png', fullPage: true });
    } else {
      console.log('No error message found, checking for question display...');
      const questionDisplay = await page.locator('.question-display').count();
      if (questionDisplay > 0) {
        console.log('✓ Question display found!');
        await page.screenshot({ path: '/tmp/console_success.png', fullPage: true });
      } else {
        console.log('✗ Question display not found');
        await page.screenshot({ path: '/tmp/console_no_question.png', fullPage: true });
      }
    }

  } catch (error) {
    console.error('\n✗ TEST FAILED:', error.message);
    await page.screenshot({ path: '/tmp/console_final_error.png', fullPage: true });
  } finally {
    console.log('\nKeeping browser open for inspection...');
    // Don't close
  }
})();
