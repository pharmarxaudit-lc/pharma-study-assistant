const { chromium } = require('playwright');

(async () => {
  console.log('=== DEBUG NEXT BUTTON ===\n');

  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Listen to console messages
  page.on('console', msg => {
    console.log(`[BROWSER]: ${msg.text()}`);
  });

  try {
    // Load and start session
    await page.goto('http://localhost:5001/#/exam', { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);

    await page.click('button:has-text("10")');
    await page.click('button:has-text("Start Session")');
    await page.waitForTimeout(2000);

    // Submit answer
    await page.click('.option:first-child');
    await page.click('button:has-text("Submit Answer")');
    await page.waitForTimeout(2000);

    // Debug: Check state
    const currentQ = await page.evaluate(() => {
      return {
        currentQuestion: window.localStorage.getItem('currentSession'),
        feedbackVisible: !!document.querySelector('.feedback-section'),
        nextButtonHTML: document.querySelector('.next-button')?.outerHTML,
        nextButtonText: document.querySelector('.next-button')?.textContent,
        nextSectionHTML: document.querySelector('.next-section')?.outerHTML,
      };
    });

    console.log('\n=== STATE CHECK ===');
    console.log('Session data:', currentQ.currentQuestion);
    console.log('Feedback visible:', currentQ.feedbackVisible);
    console.log('Next button HTML:', currentQ.nextButtonHTML);
    console.log('Next button text:', currentQ.nextButtonText);
    console.log('Next section HTML:', currentQ.nextSectionHTML);

    // Take full page screenshot
    await page.screenshot({ path: '/tmp/debug_full.png', fullPage: true });
    console.log('\nFull page screenshot: /tmp/debug_full.png');

  } catch (error) {
    console.error('Error:', error);
  }

  console.log('\nPress Ctrl+C to close.');
})();
