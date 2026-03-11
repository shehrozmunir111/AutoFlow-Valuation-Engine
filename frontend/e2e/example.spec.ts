import { test, expect } from '@playwright/test';

test('has title and can navigate', async ({ page }) => {
    await page.goto('/');

    // Expect a title "to contain" a substring.
    await expect(page).toHaveTitle(/AutoFlow Valuation Engine/i);

    // We can write more sophisticated e2e paths here for the Quote form.
    // For example:
    // await page.getByLabel('VIN').fill('1HGCM82633A00000');
    // await page.getByRole('button', { name: 'Get Quote' }).click();
    // await expect(page.getByText('Final Price')).toBeVisible();
});
