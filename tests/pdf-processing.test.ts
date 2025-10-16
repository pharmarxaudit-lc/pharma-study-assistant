import { chromium, Browser, BrowserContext, Page } from '@playwright/test';
import path from 'path';

async function testPdfProcessing(): Promise<void> {
  let browser: Browser | null = null;
  let context: BrowserContext | null = null;
  let page: Page | null = null;

  try {
    browser = await chromium.launch({ headless: false });
    context = await browser.newContext();
    page = await context.newPage();

    console.log('🌐 Navigating to http://localhost:5001...');
    await page.goto('http://localhost:5001');

    // Wait for navigation to load
    await page.waitForTimeout(1000);

    console.log('📄 Checking if Process PDFs page is visible...');

    // Check if navigation exists
    const navExists = await page.locator('.navigation').isVisible();
    console.log(`Navigation visible: ${navExists}`);

    // Check if we're on the process page or need to navigate
    const processLinkExists = await page.locator('a[href="/process"]').count();
    if (processLinkExists > 0) {
      console.log('🔗 Clicking Process PDFs link...');
      await page.click('a[href="/process"]');
      await page.waitForTimeout(500);
    }

    // Check if upload section exists
    const uploadSection = await page.locator('input[type="file"]').count();
    console.log(`Upload input found: ${uploadSection > 0}`);

    if (uploadSection > 0) {
      console.log('📤 Uploading repaso_ley_2025.pdf...');
      const pdfPath = path.join(__dirname, '..', 'uploads', '20251016_094922_repaso_ley_2025.pdf');

      // Set the file
      await page.setInputFiles('input[type="file"]', pdfPath);
      await page.waitForTimeout(1000);

      console.log('✅ File uploaded successfully');

      // Look for process button
      const processButton = page.locator('button:has-text("Process")').first();
      const processButtonExists = await processButton.count();

      if (processButtonExists > 0) {
        console.log('▶️ Clicking Process button...');
        await processButton.click();

        // Wait for processing to start
        await page.waitForTimeout(2000);

        // Check for processing status
        const bodyText = await page.textContent('body');
        if (bodyText && (bodyText.includes('Processing') || bodyText.includes('processing'))) {
          console.log('✅ PDF processing initiated successfully!');
        } else {
          console.log('⚠️ Processing may have started but status unclear');
        }

        // Take a screenshot
        await page.screenshot({ path: 'test-processing-screenshot.png' });
        console.log('📸 Screenshot saved as test-processing-screenshot.png');

      } else {
        console.log('❌ Process button not found');
      }
    } else {
      console.log('❌ Upload input not found');
    }

    // Keep browser open for 5 seconds to observe
    console.log('⏳ Keeping browser open for 5 seconds...');
    await page.waitForTimeout(5000);

  } catch (error) {
    console.error('❌ Error during test:', error instanceof Error ? error.message : String(error));
    if (page) {
      await page.screenshot({ path: 'test-error-screenshot.png' });
    }
  } finally {
    if (browser) {
      await browser.close();
    }
    console.log('✅ Test completed');
  }
}

testPdfProcessing();
