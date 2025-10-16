const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  await page.goto('http://localhost:5001/#/test', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  console.log('🔍 Finding all hidden/blank buttons across all screens\n');

  // Check each screen
  const screens = [
    { name: 'Session Config', button: '1. Session Config' },
    { name: 'Question Display', button: '2. Question Display' },
    { name: 'Results Summary', button: '3. Results Summary' }
  ];

  for (const screen of screens) {
    console.log(`=== ${screen.name.toUpperCase()} ===`);

    // Navigate to screen
    await page.click(`button:has-text("${screen.button}")`);
    await page.waitForTimeout(1000);

    // Find ALL buttons on the page
    const allButtons = await page.$$eval('button', buttons =>
      buttons.map((btn, idx) => {
        const style = window.getComputedStyle(btn);
        const text = btn.textContent.trim();
        const rect = btn.getBoundingClientRect();

        return {
          index: idx,
          text: text.substring(0, 50),
          isEmpty: text === '',
          color: style.color,
          background: style.backgroundColor,
          opacity: style.opacity,
          visible: rect.width > 0 && rect.height > 0,
          classes: btn.className,
          // Check if text is effectively invisible
          isHidden: (
            text !== '' && (
              // White on white
              (style.color === 'rgb(255, 255, 255)' && style.backgroundColor === 'rgb(255, 255, 255)') ||
              // Very low opacity
              parseFloat(style.opacity) < 0.1 ||
              // Transparent background with white text
              (style.color === 'rgb(255, 255, 255)' && style.backgroundColor === 'rgba(0, 0, 0, 0)')
            )
          )
        };
      })
    );

    // Report issues
    const hiddenButtons = allButtons.filter(btn => btn.isHidden);
    const emptyButtons = allButtons.filter(btn => btn.isEmpty);

    if (hiddenButtons.length > 0) {
      console.log('\n❌ HIDDEN TEXT BUTTONS:');
      hiddenButtons.forEach(btn => {
        console.log(`  Button ${btn.index}: "${btn.text}"`);
        console.log(`    Classes: ${btn.classes}`);
        console.log(`    Color: ${btn.color} on ${btn.background}`);
        console.log(`    Opacity: ${btn.opacity}`);
      });
    }

    if (emptyButtons.length > 0) {
      console.log('\n⚠️  EMPTY/BLANK BUTTONS:');
      emptyButtons.forEach(btn => {
        console.log(`  Button ${btn.index}: Classes: ${btn.classes}`);
      });
    }

    if (hiddenButtons.length === 0 && emptyButtons.length === 0) {
      console.log('✓ No hidden or blank buttons found');
    }

    // Take screenshot
    const filename = `/tmp/${screen.name.toLowerCase().replace(/ /g, '-')}.png`;
    await page.screenshot({ path: filename, fullPage: true });
    console.log(`📸 Screenshot: ${filename}\n`);
  }

  await browser.close();
  console.log('✅ Inspection complete!');
})();
