const { chromium } = require('playwright');

(async () => {
  console.log('Starting exam flow test...\n');

  const browser = await chromium.launch({
    headless: false,
    slowMo: 500 // Slow down actions to see what's happening
  });

  const page = await browser.newPage();

  try {
    // Navigate to the app
    console.log('1. Navigating to app...');
    await page.goto('http://localhost:5001');
    await page.waitForTimeout(1000);

    // Take screenshot of home page
    await page.screenshot({ path: '/tmp/01_home.png', fullPage: true });
    console.log('   ✓ Home page loaded');

    // Navigate to exam view
    console.log('\n2. Navigating to exam config...');
    await page.goto('http://localhost:5001/#/exam');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: '/tmp/02_exam_config.png', fullPage: true });
    console.log('   ✓ Exam config page loaded');

    // Select session type (keep default "Study")
    console.log('\n3. Configuring session...');
    console.log('   - Session type: Study (default)');

    // Select 10 questions
    console.log('   - Selecting 10 questions');
    const button10 = await page.locator('button:has-text("10")').first();
    await button10.click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: '/tmp/03_selected_10.png', fullPage: true });
    console.log('   ✓ Selected 10 questions');

    // Keep "All Topics" selected (default)
    console.log('   - Topics: All Topics (default)');

    // Click Start Session
    console.log('\n4. Starting session...');
    const startButton = await page.locator('button:has-text("Start Session")');
    await startButton.click();
    await page.waitForTimeout(2000); // Wait for API call

    // Check for errors
    const errorMessage = await page.locator('.error-message').count();
    if (errorMessage > 0) {
      const errorText = await page.locator('.error-message').textContent();
      console.log('   ✗ Error starting session:', errorText);
      await page.screenshot({ path: '/tmp/04_error.png', fullPage: true });
      throw new Error('Failed to start session: ' + errorText);
    }

    // Wait for question to load
    await page.waitForSelector('.question-display', { timeout: 5000 });
    await page.screenshot({ path: '/tmp/05_first_question.png', fullPage: true });
    console.log('   ✓ Session started, first question loaded');

    // Get question info
    const questionNumber = await page.locator('.question-number').textContent();
    const questionText = await page.locator('.question-text p').textContent();
    console.log(`\n5. Question ${questionNumber}`);
    console.log(`   "${questionText.substring(0, 80)}..."`);

    // Answer questions (loop through all 10)
    for (let i = 1; i <= 10; i++) {
      console.log(`\n6.${i} Answering question ${i}...`);

      // Select first option (A)
      const firstOption = await page.locator('.option').first();
      await firstOption.click();
      await page.waitForTimeout(300);
      console.log('   - Selected option A');

      // Submit answer
      const submitButton = await page.locator('button:has-text("Submit Answer")');
      await submitButton.click();
      await page.waitForTimeout(1500); // Wait for feedback
      await page.screenshot({ path: `/tmp/07_feedback_q${i}.png`, fullPage: true });

      // Check if answer was correct
      const feedbackHeader = await page.locator('.feedback-header');
      const isCorrect = await feedbackHeader.getAttribute('class');
      console.log(`   ✓ Answer submitted: ${isCorrect.includes('correct') ? '✓ Correct' : '✗ Incorrect'}`);

      // Check if this is the last question
      const currentQ = await page.locator('.question-number').textContent();
      const isLastQuestion = currentQ.includes('10 of 10');

      if (isLastQuestion) {
        console.log('\n7. Last question reached, clicking "View Results"...');
        const nextButton = await page.locator('button:has-text("View Results")');
        await nextButton.click();
      } else {
        // Click Next Question
        const nextButton = await page.locator('button:has-text("Next Question")');
        await nextButton.click();
      }

      await page.waitForTimeout(1000);
    }

    // Wait for results page
    console.log('\n8. Loading results...');
    await page.waitForSelector('.results-summary', { timeout: 5000 });
    await page.screenshot({ path: '/tmp/08_results.png', fullPage: true });
    console.log('   ✓ Results page loaded');

    // Get results
    const score = await page.locator('.score-number').textContent();
    const correctAnswers = await page.locator('.stat-card:has-text("Correct") .stat-value').textContent();
    const incorrectAnswers = await page.locator('.stat-card:has-text("Incorrect") .stat-value').textContent();

    console.log('\n=== TEST RESULTS ===');
    console.log(`Score: ${score}`);
    console.log(`Correct: ${correctAnswers}`);
    console.log(`Incorrect: ${incorrectAnswers}`);
    console.log('===================\n');

    console.log('✓ EXAM FLOW TEST COMPLETED SUCCESSFULLY');

  } catch (error) {
    console.error('\n✗ TEST FAILED:', error.message);
    await page.screenshot({ path: '/tmp/error_final.png', fullPage: true });

    // Log page content for debugging
    const html = await page.content();
    console.log('\n--- Page HTML ---');
    console.log(html.substring(0, 500));
    console.log('...');
  } finally {
    console.log('\nKeeping browser open for inspection...');
    console.log('Press Ctrl+C to close');
    // Don't close automatically - let user inspect
    // await browser.close();
  }
})();
