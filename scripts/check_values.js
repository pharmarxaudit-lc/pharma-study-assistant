const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  await page.goto('http://localhost:5001/#/exam', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);

  await page.click('button:has-text("10")');
  await page.click('button:has-text("Start Session")');
  await page.waitForTimeout(2000);

  // Check values before submit
  const beforeSubmit = await page.evaluate(() => {
    const questionNum = document.querySelector('.question-number')?.textContent;
    return { questionNum };
  });
  console.log('Before submit:', beforeSubmit);

  await page.click('.option:first-child');
  await page.click('button:has-text("Submit Answer")');
  await page.waitForTimeout(2000);

  // Check values after submit
  const afterSubmit = await page.evaluate(() => {
    const questionNum = document.querySelector('.question-number')?.textContent;
    const buttonText = document.querySelector('.next-button')?.textContent;
    return { questionNum, buttonText };
  });
  console.log('After submit:', afterSubmit);

  console.log('\nPress Ctrl+C to close.');
})();
