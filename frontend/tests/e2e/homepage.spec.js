import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test.describe('Homepage Tests', () => {
  test('should load homepage successfully', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveTitle(/AGTR|Merkezi/i)
  })

  test('should have no automatically detectable accessibility issues', async ({ page }) => {
    await page.goto('/')

    const accessibilityScanResults = await new AxeBuilder({ page })
      .analyze()

    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/')

    // Check if mobile menu or responsive layout is working
    await expect(page).toHaveTitle(/AGTR|Merkezi/i)
  })

  test('should navigate to different pages', async ({ page }) => {
    await page.goto('/')

    // Add your navigation tests here
    // Example: await page.click('a[href="/about"]')
    // await expect(page).toHaveURL(/.*about/)
  })
})
