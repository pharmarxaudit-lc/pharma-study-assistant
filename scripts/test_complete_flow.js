const { chromium } = require('playwright');

(async () => {
  console.log('=== COMPLETE EXAM FLOW TEST ===\n');

  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Listen to console messages
  page.on('console', msg => {
    if (msg.type() === 'log' || msg.type() === 'error') {
      console.log(`[BROWSER]: ${msg.text()}`);
    }
  });

  try {
    // 1. Load app
    console.log('1. Loading app...');
    await page.goto('http://localhost:5001/?cb=' + Date.now(), { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);
    console.log('   ✓ App loaded\n');

    // 2. Navigate to exam config
    console.log('2. Navigating to exam config...');
    await page.goto('http://localhost:5001/#/exam', { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);
    console.log('   ✓ Config page loaded\n');

    // 3. Configure session (10 questions)
    console.log('3. Configuring session...');
    await page.click('button:has-text("10")');
    console.log('   ✓ Selected 10 questions\n');

    // 4. Start session
    console.log('4. Starting session...');
    await page.click('button:has-text("Start Session")');
    await page.waitForTimeout(2000);
    console.log('   ✓ Session started\n');

    // 5. Answer questions
    for (let i = 1; i <= 10; i++) {
      console.log(`5.${i} Question ${i}...`);

      // Wait for question to load
      await page.waitForSelector('.question-text', { timeout: 5000 });

      // Select first option
      await page.click('.option:first-child');
      await page.waitForTimeout(500);

      // Submit answer
      await page.click('button:has-text("Submit Answer")');
      await page.waitForTimeout(1500);
      console.log(`   ✓ Answer submitted`);

      // Check if feedback is shown
      const feedbackVisible = await page.isVisible('.feedback-section');
      console.log(`   Feedback visible: ${feedbackVisible}`);

      // Check if next button exists
      const nextButtonVisible = await page.isVisible('button:has-text("Next Question")');
      const viewResultsVisible = await page.isVisible('button:has-text("View Results")');
      console.log(`   Next button visible: ${nextButtonVisible}`);
      console.log(`   View Results visible: ${viewResultsVisible}`);

      if (i < 10) {
        // Click next question
        if (nextButtonVisible) {
          await page.click('button:has-text("Next Question")');
          await page.waitForTimeout(1000);
          console.log(`   ✓ Moved to next question\n`);
        } else {
          console.log(`   ❌ Next button not found!\n`);
          throw new Error('Next button not found');
        }
      } else {
        // Last question - click View Results
        if (viewResultsVisible) {
          await page.click('button:has-text("View Results")');
          await page.waitForTimeout(2000);
          console.log(`   ✓ Clicked View Results\n`);
        } else {
          console.log(`   ❌ View Results button not found!\n`);
          throw new Error('View Results button not found');
        }
      }
    }

    // 6. Check results page
    console.log('6. Checking results...');
    const resultsVisible = await page.isVisible('.results-summary');
    if (resultsVisible) {
      console.log('   ✓ Results page displayed\n');
      console.log('✅ TEST PASSED: Complete exam flow works!');
    } else {
      console.log('   ❌ Results page not found\n');
      throw new Error('Results page not displayed');
    }

    // Take screenshot
    await page.screenshot({ path: '/tmp/final_results.png' });
    console.log('\nScreenshot saved to /tmp/final_results.png');

  } catch (error) {
    console.error('\n❌ TEST FAILED:', error.message);
    await page.screenshot({ path: '/tmp/test_error.png' });
    console.log('Error screenshot saved to /tmp/test_error.png');
  }

  console.log('\nBrowser left open for inspection. Press Ctrl+C to close.');
  // Keep browser open for inspection
  // await browser.close();
})();
