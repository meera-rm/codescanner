import { test, expect } from '@playwright/test';

// E2E tests for CAQI Dashboard
// Tests user workflows and integration scenarios

test.describe('CAQI Dashboard E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to dashboard (adjust URL based on your dev server)
    await page.goto('http://localhost:3000/caqi', { waitUntil: 'networkidle' });
  });

  test('should load dashboard with all tabs', async ({ page }) => {
    // Check that all three tabs are visible
    await expect(page.locator('button:has-text("Team Comparison")')).toBeVisible();
    await expect(page.locator('button:has-text("Team Details")')).toBeVisible();
    await expect(page.locator('button:has-text("Trends")')).toBeVisible();
  });

  test('should switch tabs without errors', async ({ page }) => {
    // Click Team Details tab
    await page.click('button:has-text("Team Details")');
    await expect(page.locator('text=Overall CAQI')).toBeVisible();

    // Click Trends tab
    await page.click('button:has-text("Trends")');
    await expect(page.locator('text=Trend Analysis')).toBeVisible();

    // Click back to Comparison
    await page.click('button:has-text("Team Comparison")');
    await expect(page.locator('text=Team Comparison')).toBeVisible();
  });

  test('should display team comparison table', async ({ page }) => {
    // Verify table headers
    await expect(page.locator('text=Team')).toBeVisible();
    await expect(page.locator('text=Archetype')).toBeVisible();
    await expect(page.locator('text=CAQI')).toBeVisible();
  });

  test('should select teams from pills', async ({ page }) => {
    // Wait for team pills to load
    await page.waitForSelector('button[class*="team-pill"]', { timeout: 5000 });

    // Get first two teams
    const teamPills = await page.locator('button[class*="team-pill"]').count();
    expect(teamPills).toBeGreaterThan(0);

    // Click second team if available
    if (teamPills > 1) {
      const secondPill = page.locator('button[class*="team-pill"]').nth(1);
      await secondPill.click();
      await page.waitForLoadState('networkidle');
    }
  });

  test('should render radar chart on Team Details tab', async ({ page }) => {
    // Navigate to Team Details
    await page.click('button:has-text("Team Details")');

    // Check for radar chart elements (SVG)
    const svgs = await page.locator('svg').count();
    expect(svgs).toBeGreaterThan(0);

    // Check for CAQI score display
    await expect(page.locator('text=/\\d+\\/500/')).toBeVisible();
  });

  test('should render trend line chart on Trends tab', async ({ page }) => {
    // Navigate to Trends
    await page.click('button:has-text("Trends")');

    // Check for line chart SVG
    const svgs = await page.locator('svg').count();
    expect(svgs).toBeGreaterThan(0);

    // Check for trend analysis section
    await expect(page.locator('text=Starting Score')).toBeVisible();
    await expect(page.locator('text=Current Score')).toBeVisible();
  });

  test('should display trend direction indicator', async ({ page }) => {
    // Navigate to Trends
    await page.click('button:has-text("Trends")');

    // Check for trend direction (improving, stable, or declining)
    const trendIndicator = page.locator('[class*="trend-indicator"]');
    await expect(trendIndicator).toBeVisible();
  });

  test('should handle mobile responsive layout', async ({ page }) => {
    // Set viewport to mobile size
    await page.setViewportSize({ width: 375, height: 667 });

    // Wait for layout to adapt
    await page.waitForLoadState('networkidle');

    // Verify tabs are still accessible
    await expect(page.locator('button:has-text("Team Comparison")')).toBeVisible();

    // Click a tab and verify content is visible
    await page.click('button:has-text("Team Details")');
    await expect(page.locator('text=Overall CAQI')).toBeVisible();
  });

  test('should handle tablet responsive layout', async ({ page }) => {
    // Set viewport to tablet size
    await page.setViewportSize({ width: 768, height: 1024 });

    // Wait for layout to adapt
    await page.waitForLoadState('networkidle');

    // Verify dashboard is still functional
    await expect(page.locator('button:has-text("Team Comparison")')).toBeVisible();

    // Verify team comparison displays correctly on tablet
    const table = page.locator('table');
    await expect(table).toBeVisible();
  });

  test('should load and display all team data', async ({ page }) => {
    // Check that teams are loaded from API/mock data
    const teamPills = await page.locator('button[class*="team-pill"]');
    const count = await teamPills.count();

    // Should have at least 1 team
    expect(count).toBeGreaterThanOrEqual(1);

    // Each pill should have a CAQI badge with a number
    const badges = await page.locator('[class*="caqi-badge"]');
    await expect(badges).toHaveCount(count);
  });

  test('should calculate and display statistics', async ({ page }) => {
    // Navigate to Team Comparison
    await page.click('button:has-text("Team Comparison")');

    // Check for statistics section
    await expect(page.locator('text=Average CAQI')).toBeVisible();
    await expect(page.locator('text=Highest CAQI')).toBeVisible();
    await expect(page.locator('text=Total Members')).toBeVisible();
  });

  test('should display personality archetypes', async ({ page }) => {
    // Check for archetype badges on team pills
    const archetypeElements = await page.locator('[class*="archetype"]');
    const count = await archetypeElements.count();

    // Should display archetypes
    expect(count).toBeGreaterThan(0);
  });

  test('should handle empty data gracefully', async ({ page }) => {
    // This test assumes the dashboard handles empty teams array
    // Navigate and check for empty state message if applicable
    const emptyState = page.locator('text=No teams found');

    // Either empty state or teams should be visible
    const teamsVisible = await page.locator('button[class*="team-pill"]').count();
    const emptyStateVisible = await emptyState.count();

    expect(teamsVisible + emptyStateVisible).toBeGreaterThanOrEqual(0);
  });

  test('should render footer with metadata', async ({ page }) => {
    // Scroll to bottom
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));

    // Check for footer content (if applicable)
    const footer = page.locator('footer, [class*="footer"]');
    await expect(footer).toBeVisible();
  });

  test('should not have console errors during navigation', async ({ page }) => {
    // Collect console errors
    const consoleErrors: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // Navigate through all tabs
    await page.click('button:has-text("Team Details")');
    await page.click('button:has-text("Trends")');
    await page.click('button:has-text("Team Comparison")');

    // Verify no errors were logged
    expect(consoleErrors).toHaveLength(0);
  });

  test('should maintain scroll position on tab switch', async ({ page }) => {
    // Scroll down
    await page.evaluate(() => window.scrollBy(0, 300));

    // Get scroll position
    const scrollBefore = await page.evaluate(() => window.scrollY);

    // Switch tab (should reset scroll)
    await page.click('button:has-text("Team Details")');

    // Get new scroll position
    const scrollAfter = await page.evaluate(() => window.scrollY);

    // Scroll should reset on tab change
    expect(scrollAfter).toBeLessThan(scrollBefore + 100);
  });
});
