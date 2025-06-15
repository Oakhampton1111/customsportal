import { chromium, FullConfig } from '@playwright/test';

declare global {
  interface Window {
    __PLAYWRIGHT_TEST__?: boolean;
  }
}

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting global setup for Playwright E2E tests...');
  
  // Start a browser instance to warm up
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    // Wait for the development server to be ready
    console.log('⏳ Waiting for development server...');
    const baseURL = config.projects[0].use.baseURL || 'http://localhost:5173';
    
    // Try to connect to the server with retries
    let retries = 30;
    while (retries > 0) {
      try {
        await page.goto(baseURL, { timeout: 5000 });
        console.log('✅ Development server is ready');
        break;
      } catch {
        retries--;
        if (retries === 0) {
          throw new Error(`Failed to connect to development server at ${baseURL}`);
        }
        await page.waitForTimeout(2000);
      }
    }
    
    // Perform any global setup tasks
    console.log('🔧 Performing global setup tasks...');
    
    // Clear any existing local storage/session storage
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    
    // Set up any global test data or configurations
    await page.evaluate(() => {
      // Set test environment flag
      window.__PLAYWRIGHT_TEST__ = true;
      
      // Disable animations for consistent testing
      const style = document.createElement('style');
      style.textContent = `
        *, *::before, *::after {
          animation-duration: 0s !important;
          animation-delay: 0s !important;
          transition-duration: 0s !important;
          transition-delay: 0s !important;
        }
      `;
      document.head.appendChild(style);
    });
    
    console.log('✅ Global setup completed successfully');
    
  } catch (error) {
    console.error('❌ Global setup failed:', error);
    throw error;
  } finally {
    await context.close();
    await browser.close();
  }
}

export default globalSetup;