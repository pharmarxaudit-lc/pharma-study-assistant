const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  await page.goto('http://localhost:5001/#/test', { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);

  // Take screenshot
  await page.screenshot({ path: '/tmp/test-screen.png', fullPage: true });
  console.log('Screenshot saved to /tmp/test-screen.png');

  // Get HTML
  const html = await page.content();
  console.log('\n=== PAGE HTML (first 2000 chars) ===');
  console.log(html.substring(0, 2000));

  await browser.close();
})();
