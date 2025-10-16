const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  await page.goto('http://localhost:5001/#/test', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  console.log('🔍 Inspecting Mock Screens for blank text issues\n');

  // Screen 1: Session Config
  console.log('=== SCREEN 1: Session Config ===');
  await page.click('button:has-text("1. Session Config")');
  await page.waitForTimeout(1000);

  // Check all buttons for empty/blank text
  const configButtons = await page.$$eval('.session-config button', buttons =>
    buttons.map((btn, idx) => ({
      index: idx,
      text: btn.textContent.trim(),
      isEmpty: btn.textContent.trim() === '',
      classes: btn.className,
      computed: window.getComputedStyle(btn).color
    }))
  );

  console.log('\nButtons found:');
  configButtons.forEach(btn => {
    if (btn.isEmpty || btn.text === '') {
      console.log(`  ❌ Button ${btn.index}: EMPTY/BLANK`);
      console.log(`     Classes: ${btn.classes}`);
      console.log(`     Color: ${btn.computed}`);
    } else if (btn.text.length < 5) {
      console.log(`  ⚠️  Button ${btn.index}: "${btn.text}" (very short)`);
    }
  });

  // Take screenshot
  await page.screenshot({ path: '/tmp/inspect-config.png', fullPage: true });
  console.log('  📸 Saved: /tmp/inspect-config.png\n');

  // Screen 2: Question Display
  console.log('=== SCREEN 2: Question Display ===');
  await page.click('button:has-text("2. Question Display")');
  await page.waitForTimeout(1000);

  const questionButtons = await page.$$eval('.question-display button', buttons =>
    buttons.map((btn, idx) => ({
      index: idx,
      text: btn.textContent.trim(),
      isEmpty: btn.textContent.trim() === '',
      classes: btn.className
    }))
  );

  console.log('\nButtons found:');
  questionButtons.forEach(btn => {
    if (btn.isEmpty || btn.text === '') {
      console.log(`  ❌ Button ${btn.index}: EMPTY/BLANK`);
      console.log(`     Classes: ${btn.classes}`);
    }
  });

  await page.screenshot({ path: '/tmp/inspect-question.png', fullPage: true });
  console.log('  📸 Saved: /tmp/inspect-question.png\n');

  // Screen 3: Results Summary
  console.log('=== SCREEN 3: Results Summary ===');
  await page.click('button:has-text("3. Results Summary")');
  await page.waitForTimeout(1000);

  const resultsButtons = await page.$$eval('.results-summary button', buttons =>
    buttons.map((btn, idx) => ({
      index: idx,
      text: btn.textContent.trim(),
      isEmpty: btn.textContent.trim() === '',
      classes: btn.className
    }))
  );

  console.log('\nButtons found:');
  resultsButtons.forEach(btn => {
    if (btn.isEmpty || btn.text === '') {
      console.log(`  ❌ Button ${btn.index}: EMPTY/BLANK`);
      console.log(`     Classes: ${btn.classes}`);
    }
  });

  await page.screenshot({ path: '/tmp/inspect-results.png', fullPage: true });
  console.log('  📸 Saved: /tmp/inspect-results.png\n');

  // Check for elements with CSS that might hide text
  console.log('=== Checking for CSS issues ===');
  await page.goto('http://localhost:5001/#/test', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);

  const hiddenTextElements = await page.$$eval('button, .button, [class*="button"]', elements =>
    elements.filter(el => {
      const style = window.getComputedStyle(el);
      const text = el.textContent.trim();
      return (
        text !== '' &&
        (style.color === 'rgb(255, 255, 255)' || // white text
         style.opacity === '0' ||
         style.visibility === 'hidden' ||
         parseFloat(style.fontSize) < 1)
      );
    }).map(el => ({
      text: el.textContent.trim().substring(0, 30),
      color: window.getComputedStyle(el).color,
      background: window.getComputedStyle(el).backgroundColor,
      opacity: window.getComputedStyle(el).opacity,
      fontSize: window.getComputedStyle(el).fontSize
    }))
  );

  if (hiddenTextElements.length > 0) {
    console.log('Found elements with potential visibility issues:');
    hiddenTextElements.forEach((el, idx) => {
      console.log(`  ${idx + 1}. "${el.text}"`);
      console.log(`     Color: ${el.color} on ${el.background}`);
      console.log(`     Opacity: ${el.opacity}, Font: ${el.fontSize}`);
    });
  } else {
    console.log('✓ No obvious CSS visibility issues found');
  }

  await browser.close();
  console.log('\n✅ Inspection complete!');
})();
