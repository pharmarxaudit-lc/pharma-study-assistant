const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  page.on('console', msg => {
    console.log(`[BROWSER]: ${msg.text()}`);
  });

  await page.goto('http://localhost:5001/#/exam', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);

  // Start session with 1 question only
  await page.evaluate(() => {
    const numQuestionsInput = document.querySelector('input[type="number"]');
    if (numQuestionsInput) {
      numQuestionsInput.value = '1';
    }
  });

  // Select 10 questions
  await page.click('button:has-text("10")');
  await page.click('button:has-text("Start Session")');
  await page.waitForTimeout(2000);

  // Answer all 10 questions quickly
  for (let i = 0; i < 10; i++) {
    await page.click('.option:first-child');
    await page.click('button:has-text("Submit Answer")');
    await page.waitForTimeout(1500);

    // Check the last API response
    const apiResponse = await page.evaluate(() => {
      return window.lastApiResponse;
    });

    if (i === 9) {
      console.log('\n=== LAST QUESTION RESPONSE ===');
      console.log('session_complete:', apiResponse?.session_complete);
      console.log('next_question:', apiResponse?.next_question);
    }

    if (i < 9) {
      await page.click('button:has-text("Next Question")');
      await page.waitForTimeout(1000);
    }
  }

  console.log('\nPress Ctrl+C to close.');
})();
