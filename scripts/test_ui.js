// Quick Playwright script to test the mock screens
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    console.log('🔍 Testing UI at http://localhost:5001/#/test');

    // Navigate to test page (using hash router)
    await page.goto('http://localhost:5001/#/test', { waitUntil: 'networkidle' });

    // Wait for the page to load
    await page.waitForTimeout(2000);

    // Get page title
    const title = await page.title();
    console.log('✓ Page title:', title);

    // Check for screen navigation buttons
    const buttons = await page.$$eval('.screen-nav button', btns =>
      btns.map(b => b.textContent.trim())
    );
    console.log('✓ Navigation buttons found:', buttons);

    // Test Screen 1: Session Config
    console.log('\n📋 Testing Screen 1: Session Config');
    await page.click('button:has-text("1. Session Config")');
    await page.waitForTimeout(1000);

    const configHeading = await page.textContent('h2');
    console.log('  - Heading:', configHeading);

    const hasEnglishUI = configHeading.includes('Configure') || configHeading.includes('Session');
    console.log('  - English UI:', hasEnglishUI ? '✓ YES' : '✗ NO');

    // Test Screen 2: Question Display
    console.log('\n📝 Testing Screen 2: Question Display');
    await page.click('button:has-text("2. Question Display")');
    await page.waitForTimeout(1000);

    const questionText = await page.textContent('.question-number');
    console.log('  - Question indicator:', questionText);

    const hasSubmitButton = await page.$('button:has-text("Submit Answer")');
    console.log('  - Submit button:', hasSubmitButton ? '✓ Found' : '✗ Not found');

    // Test Screen 3: Results Summary
    console.log('\n🎯 Testing Screen 3: Results Summary');
    await page.click('button:has-text("3. Results Summary")');
    await page.waitForTimeout(1000);

    const scoreExists = await page.$('.score-circle');
    console.log('  - Score circle:', scoreExists ? '✓ Found' : '✗ Not found');

    const statsCards = await page.$$('.stat-card');
    console.log('  - Stats cards found:', statsCards.length);

    // Take screenshots
    console.log('\n📸 Taking screenshots...');
    await page.click('button:has-text("1. Session Config")');
    await page.waitForTimeout(500);
    await page.screenshot({ path: '/tmp/screen1-config.png', fullPage: true });
    console.log('  ✓ Saved: /tmp/screen1-config.png');

    await page.click('button:has-text("2. Question Display")');
    await page.waitForTimeout(500);
    await page.screenshot({ path: '/tmp/screen2-question.png', fullPage: true });
    console.log('  ✓ Saved: /tmp/screen2-question.png');

    await page.click('button:has-text("3. Results Summary")');
    await page.waitForTimeout(500);
    await page.screenshot({ path: '/tmp/screen3-results.png', fullPage: true });
    console.log('  ✓ Saved: /tmp/screen3-results.png');

    console.log('\n✅ All tests completed successfully!');

  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
