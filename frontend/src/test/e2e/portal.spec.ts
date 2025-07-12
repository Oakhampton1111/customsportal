import { test, expect } from '@playwright/test';

test.describe('Customer Portal', () => {
  test.beforeEach(async ({ page }) => {
    // Mock API responses
    await page.route('/api/auth/me', async route => {
      await route.fulfill({
        json: {
          id: '1',
          email: 'test@example.com',
          name: 'Test User',
          role: 'customer',
        },
      });
    });

    await page.route('/api/jobs', async route => {
      await route.fulfill({
        json: {
          jobs: [
            {
              id: '1',
              reference: 'JOB-001',
              status: 'in_progress',
              type: 'import',
              description: 'Test import job',
              created_at: '2024-01-01T00:00:00Z',
            },
          ],
          total: 1,
          page: 1,
          per_page: 10,
        },
      });
    });
  });

  test('should load the portal dashboard', async ({ page }) => {
    await page.goto('/portal');
    
    // Check if the portal layout is loaded
    await expect(page.locator('[data-testid="portal-layout"]')).toBeVisible();
    
    // Check if the sidebar is present
    await expect(page.locator('[data-testid="portal-sidebar"]')).toBeVisible();
    
    // Check if the main content area is present
    await expect(page.locator('[data-testid="portal-main"]')).toBeVisible();
  });

  test('should navigate between portal pages', async ({ page }) => {
    await page.goto('/portal');
    
    // Navigate to Jobs page
    await page.click('[data-testid="nav-jobs"]');
    await expect(page).toHaveURL('/portal/jobs');
    await expect(page.locator('h1')).toContainText('Jobs');
    
    // Navigate to Documents page
    await page.click('[data-testid="nav-documents"]');
    await expect(page).toHaveURL('/portal/documents');
    await expect(page.locator('h1')).toContainText('Documents');
    
    // Navigate to Payments page
    await page.click('[data-testid="nav-payments"]');
    await expect(page).toHaveURL('/portal/payments');
    await expect(page.locator('h1')).toContainText('Payments');
    
    // Navigate to Support page
    await page.click('[data-testid="nav-support"]');
    await expect(page).toHaveURL('/portal/support');
    await expect(page.locator('h1')).toContainText('Support');
  });

  test('should display jobs list', async ({ page }) => {
    await page.goto('/portal/jobs');
    
    // Wait for jobs to load
    await expect(page.locator('[data-testid="jobs-list"]')).toBeVisible();
    
    // Check if job item is displayed
    await expect(page.locator('[data-testid="job-item-1"]')).toBeVisible();
    await expect(page.locator('[data-testid="job-item-1"]')).toContainText('JOB-001');
    await expect(page.locator('[data-testid="job-item-1"]')).toContainText('in_progress');
  });

  test('should handle responsive design', async ({ page }) => {
    // Test desktop view
    await page.setViewportSize({ width: 1200, height: 800 });
    await page.goto('/portal');
    
    // Sidebar should be visible on desktop
    await expect(page.locator('[data-testid="portal-sidebar"]')).toBeVisible();
    
    // Test mobile view
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Sidebar should be hidden on mobile (or collapsed)
    const sidebar = page.locator('[data-testid="portal-sidebar"]');
    const isHidden = await sidebar.isHidden();
    const hasCollapsedClass = await sidebar.getAttribute('class');
    
    expect(isHidden || hasCollapsedClass?.includes('collapsed')).toBeTruthy();
  });

  test('should handle authentication state', async ({ page }) => {
    // Test unauthenticated state
    await page.route('/api/auth/me', async route => {
      await route.fulfill({
        status: 401,
        json: { error: 'Unauthorized' },
      });
    });

    await page.goto('/portal');
    
    // Should redirect to login or show login form
    await expect(page).toHaveURL(/\/(login|auth)/);
  });

  test('should search and filter jobs', async ({ page }) => {
    await page.goto('/portal/jobs');
    
    // Wait for jobs to load
    await expect(page.locator('[data-testid="jobs-list"]')).toBeVisible();
    
    // Test search functionality
    const searchInput = page.locator('[data-testid="jobs-search"]');
    if (await searchInput.isVisible()) {
      await searchInput.fill('JOB-001');
      await expect(page.locator('[data-testid="job-item-1"]')).toBeVisible();
      
      await searchInput.fill('nonexistent');
      await expect(page.locator('[data-testid="job-item-1"]')).toBeHidden();
    }
  });

  test('should handle error states gracefully', async ({ page }) => {
    // Mock API error
    await page.route('/api/jobs', async route => {
      await route.fulfill({
        status: 500,
        json: { error: 'Internal Server Error' },
      });
    });

    await page.goto('/portal/jobs');
    
    // Should show error message
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]')).toContainText('error');
  });
});

test.describe('Portal Accessibility', () => {
  test('should be accessible', async ({ page }) => {
    await page.goto('/portal');
    
    // Check for proper heading structure
    const h1 = await page.locator('h1').count();
    expect(h1).toBeGreaterThan(0);
    
    // Check for proper navigation landmarks
    await expect(page.locator('nav')).toBeVisible();
    await expect(page.locator('main')).toBeVisible();
    
    // Check for proper form labels (if any forms are present)
    const inputs = await page.locator('input').count();
    if (inputs > 0) {
      const labels = await page.locator('label').count();
      expect(labels).toBeGreaterThan(0);
    }
  });

  test('should support keyboard navigation', async ({ page }) => {
    await page.goto('/portal');
    
    // Test tab navigation
    await page.keyboard.press('Tab');
    const focusedElement = await page.locator(':focus');
    await expect(focusedElement).toBeVisible();
    
    // Test navigation with Enter key
    await page.keyboard.press('Enter');
    // Should navigate or activate the focused element
  });
});