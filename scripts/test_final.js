const { chromium } = require('playwright');

(async () => {
  console.log('=== FINAL EXAM FLOW TEST ===\n');

  const browser = await chromium.launch({
    headless: false,
    slowMo: 300
  });

  const context = await browser.newContext({
    // Disable cache
    ignoreHTTPSErrors: true,
  });

  const page = await context.newPage();

  // Clear storage
  await context.clearCookies();

  // Capture console
  page.on('console', msg => {
    if (msg.text().includes('Starting session') || msg.text().includes('ERROR') || msg.text().includes('Failed')) {
      console.log(`[BROWSER]:`, msg.text());
    }
  });

  try {
    console.log('1. Loading app with cache bypass...');
    // Add cache-busting parameter
    await page.goto('http://localhost:5001/?cb=' + Date.now(), {
      waitUntil: 'networkidle',
      timeout: 10000
    });
    await page.waitForTimeout(1000);
    console.log('   ✓ App loaded\n');

    console.log('2. Navigating to exam config...');
    await page.goto('http://localhost:5001/#/exam?cb=' + Date.now(), { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);
    await page.screenshot({ path: '/tmp/step1_config.png', fullPage: true });
    console.log('   ✓ Config page loaded\n');

    console.log('3. Configuring session...');
    console.log('   - Selecting 10 questions');
    await page.click('button:has-text("10")');
    await page.waitForTimeout(500);
    console.log('   ✓ Selected 10 questions\n');

    console.log('4. Starting session...');
    await page.click('button:has-text("Start Session")');
    await page.waitForTimeout(3000);

    // Check for errors
    const hasError = await page.locator('.error-message').count() > 0;
    if (hasError) {
      const errorText = await page.locator('.error-message').textContent();
      await page.screenshot({ path: '/tmp/step2_error.png', fullPage: true });
      throw new Error(`Session start failed: ${errorText}`);
    }

    // Wait for question display
    await page.waitForSelector('.question-display', { timeout: 5000 });
    await page.screenshot({ path: '/tmp/step3_question1.png', fullPage: true });
    console.log('   ✓ Session started, first question loaded\n');

    // Answer 10 questions
    for (let i = 1; i <= 10; i++) {
      console.log(`5.${i} Question ${i}...`);

      // Select first option
      await page.locator('.option').first().click();
      await page.waitForTimeout(300);

      // Submit
      await page.click('button:has-text("Submit Answer")');
      await page.waitForTimeout(1500);

      const feedbackEl = await page.locator('.feedback-header');
      const feedbackClass = await feedbackEl.getAttribute('class');
      console.log(`   ${feedbackClass.includes('correct') ? '✓' : '✗'} Answer submitted\n`);

      // Check if last question
      const questionNum = await page.locator('.question-number').textContent();
      if (questionNum.includes('10 of 10')) {
        console.log('6. Last question - clicking View Results...');
        await page.click('button:has-text("View Results")');
        break;
      } else {
        await page.click('button:has-text("Next Question")');
      }

      await page.waitForTimeout(1000);
    }

    // Wait for results
    console.log('\n7. Loading results...');
    await page.waitForSelector('.results-summary', { timeout: 5000 });
    await page.screenshot({ path: '/tmp/step4_results.png', fullPage: true });

    const score = await page.locator('.score-number').textContent();
    const correct = await page.locator('.stat-card:has-text("Correct") .stat-value').textContent();
    const incorrect = await page.locator('.stat-card:has-text("Incorrect") .stat-value').textContent();

    console.log('\n=== TEST COMPLETED SUCCESSFULLY ===');
    console.log(`Final Score: ${score}`);
    console.log(`Correct: ${correct}`);
    console.log(`Incorrect: ${incorrect}`);
    console.log('===================================\n');

  } catch (error) {
    console.error('\n❌ TEST FAILED:', error.message);
    await page.screenshot({ path: '/tmp/error_screenshot.png', fullPage: true });
  } finally {
    console.log('Browser left open for inspection. Press Ctrl+C to close.');
    // Keep open
  }
})();
