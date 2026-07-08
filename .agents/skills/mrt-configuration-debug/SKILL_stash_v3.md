---
name: mrt-configuration-debug
description: Debug missing Material React Table (MRT) toolbar features — identify the controlling enable* prop, fix false→true, check renderToolbarInternalActions, and verify with playwright-cli.
category: Debugging & Verification
---

# MRT Configuration Debug

Debug missing Material React Table (MRT) toolbar features by identifying the
controlling `enable*` prop, changing it from `false` to `true`, checking whether
`renderToolbarInternalActions` overrides omit the corresponding component, and
verifying the fix on a running dev server with playwright-cli.

## When to use

Use this skill when debugging a Material React Table (MRT) page where a built-in toolbar feature (density toggle, fullscreen button, column filters, show/hide columns, global filter, row selection, column ordering, etc.) is not visible or not working as expected. This includes:

- density toggle button not appearing in the toolbar
- fullscreen button not showing
- column filters unexpectedly hidden
- show/hide columns menu not accessible
- global filter bar missing
- enable\* config options not taking effect
- verifying fixes using playwright-cli on a running dev server

## What the skill owns

- identifying the `enable*` toggle props in `useMaterialReactTable({...})` that control built-in feature visibility
- mapping each MRT component (MRT_ToggleDensePaddingButton, MRT_ToggleFullScreenButton, MRT_ToggleFiltersButton, etc.) to its controlling `enable*` prop
- fixing `false` → `true` for the relevant `enable*` prop
- checking whether `renderToolbarInternalActions` is overridden (which may omit or include the affected component)
- verifying fixes on a running dev server using playwright-cli

## Environment & Dependencies

- **@playwright/test ^1.60.0**: Required for Step 6 E2E test verification.
  Verify with `npx playwright --version`. Install with `npx playwright install chromium`.
- **playwright-cli**: Required for Step 5 verification. Verify with `playwright-cli --version`.
  If not available, install globally: `npm install -g @playwright/cli@latest`, or use
  `npx --no-install playwright-cli` for a local invocation.
- **grep / ripgrep**: Required for the scripted audit in `scripts/`. Verify with `grep --version`
  or `rg --version`.
- **Python 3.12+**: Required to run `scripts/find-mrt-config-issues.py`. Verify with `python3 --version`.

## Common MRT feature toggles and their controlling props

| Feature | Controlling prop | Component |
|---------|-----------------|-----------|
| Density toggle | `enableDensityToggle` | `MRT_ToggleDensePaddingButton` |
| Fullscreen toggle | `enableFullScreenToggle` | `MRT_ToggleFullScreenButton` |
| Column filters | `enableColumnFilters` | (built-in filter row) |
| Show/hide columns | `enableHiding` | `MRT_ShowHideColumnsButton` |
| Filter button | (always rendered when present) | `MRT_ToggleFiltersButton` |
| Column ordering | `enableColumnOrdering` | (column drag-and-drop) |
| Global filter | `enableGlobalFilter` | (built-in search bar) |
| Row selection | `enableRowSelection` | checkbox column |
| Grouping | `enableGrouping` | `MRT_ToggleGroupingButton` |

## Debugging workflow

### Step 1: Identify the missing feature

The user reports a specific toolbar button or feature is not visible. Take note of which one (density, fullscreen, filters, columns menu, etc.).

### Step 2: Read the source file

Open the `Table*.tsx` file. Locate the `useMaterialReactTable({...})` call. Search for the
relevant `enable*` prop (see the table in the previous section).

If the prop is set to `false`, that is the root cause. If the prop is absent, the default is
`true` in MRT V2 — look for other causes.

**Automated cross-file scan**: To audit all table files in one pass, use the helper script:

```bash
python3 scripts/find-mrt-config-issues.py --glob "src/Pages/**/Table*.tsx"
```

This scans every matched file for all known `enable*` props and outputs a markdown
table showing which are `❌ false` and which are `✅ true`. Example output:

```text
| File | enableDensityToggle | enableFullScreenToggle | … |
| :--- | :--- | :--- | :--- |
| `src/Pages/Broker/TableBroker.tsx` | ❌ | — | … |
| `src/Pages/Unit/TableUnit.tsx` | ✅ | — | … |
```

Also supports `--format json` for programmatic consumption.

### Step 3: Check renderToolbarInternalActions

If the `renderToolbarInternalActions` function is overridden, verify that the expected component (e.g., `<MRT_ToggleDensePaddingButton table={table} />`) is included in the JSX return. If the override omits it, add it back.

If `renderToolbarInternalActions` is NOT overridden, MRT's default internal toolbar renders the feature button automatically when the corresponding `enable*` prop is `true`.

### Step 4: Fix

Change the `enable*` prop from `false` to `true`. Example:

```tsx
// Before:
enableDensityToggle: false,

// After:
enableDensityToggle: true,
```

If the component is also missing from an overridden `renderToolbarInternalActions`, add it:

```tsx
renderToolbarInternalActions: ({ table }) => (
  <Box sx={{ display: 'flex', alignItems: 'center' }}>
    <MRT_ToggleFiltersButton table={table} />
    <MRT_ShowHideColumnsButton table={table} />
    <MRT_ToggleDensePaddingButton table={table} />  {/* add this line if missing */}
    <MRT_ToggleFullScreenButton table={table} />
  </Box>
),
```

### Step 5: Verify with playwright-cli

After applying the fix, use playwright-cli to verify the button appears on the live page:

```bash
# 1. Attach to Chrome via Playwright extension
playwright-cli attach --extension=chrome

# 2. Navigate to the page
playwright-cli -s=chrome goto "http://localhost:3000/<page-route>"

# 3. Check for the specific button by aria-label
playwright-cli -s=chrome --raw eval "Array.from(document.querySelectorAll('button')).filter(b => (b.getAttribute('aria-label') || '').toLowerCase().includes('density')).map(b => ({ 'aria-label': b.getAttribute('aria-label') }))"
```

Expected output for density toggle:

```json
[{"aria-label": "Toggle Density (comfortable)"}]
```

You can also verify the button can be clicked:

```ts
const btn = Array.from(document.querySelectorAll('button')).find(b =>
  (b.getAttribute('aria-label') || '').toLowerCase().includes('density')
);
if (btn) btn.click();
```

### Step 6: Verify with Playwright E2E Tests

Beyond quick `playwright-cli` inspection, write proper Playwright E2E tests
that assert MRT features work end-to-end. This approach verifies the feature
is not only rendered but also interactive, and catches regressions on every
test run.

#### 6.1 Toolbar feature visibility

Use `getByRole` or `getByLabel` to locate MRT toolbar buttons:

```typescript
await expect(page.getByLabel(/Density/i)).toBeVisible();
await expect(page.getByLabel(/Fullscreen/i)).toBeVisible();
```

#### 6.2 Column filter verification

Column filter inputs appear when `enableColumnFilters` is `true` (or
`showColumnFilters` is `true` in the state). After a full page reload
`showColumnFilters` defaults to `true` (React `useState(true)` is not
persisted on first load).

```typescript
// Apply a text filter by typing + pressing Enter to commit
const statusFilter = page.getByPlaceholder('Filter by Status');
await statusFilter.fill('pending');
await statusFilter.press('Enter');
// Verify the filtering indicator icon in the column header
await expect(
  page.getByRole('columnheader', { name: /Status/i }).first()
    .getByRole('button', { name: /filtering/i })
).toBeVisible();

// Clear by emptying + Enter
await statusFilter.fill('');
await statusFilter.press('Enter');
// Confirm indicator is gone
await expect(
  page.getByRole('columnheader', { name: /Status/i }).first()
    .getByRole('button', { name: /filtering/i })
).not.toBeVisible();
```

**Note**: Using `Escape` key does NOT clear MRT column filters — it only
closes the filter mode popover. Use `fill('')` + `press('Enter')` instead.

#### 6.3 Sorting verification

Click a column header to toggle sorting. The sort indicator is an arrow
icon rendered inside the column header:

```typescript
const statusHeader = page.getByRole('columnheader', { name: /Status/i }).first();
const sortBtn = statusHeader.getByRole('button').first();
await sortBtn.click();
// Wait for sort to apply
await page.waitForTimeout(500);
// Confirm sort indicator (MRT renders an SVG arrow icon when sorted)
const sortedIcon = statusHeader.locator('[data-testid*="Arrow"]').first();
await expect(sortedIcon).toBeVisible();
```

#### 6.4 Pagination verification

The Next/Previous buttons may be disabled when only one page of data exists:

```typescript
const nextBtn = page.getByRole('button', { name: /Next/i }).first();
if (await nextBtn.isVisible() && await nextBtn.isEnabled()) {
  await nextBtn.click();
  // Confirm page changed and table re-rendered
  await expect(page.getByText(/Filters/i)).toBeVisible();
}
```

#### 6.5 Export verification

CSV download triggers a file download event; Excel uses a different flow:

```typescript
// CSV: listen for download event
const download = await page.waitForEvent('download');
// assertion
expect(download.suggestedFilename()).toMatch(/\.csv$/i);

// Excel: button may trigger a server-side action; assert the button exists
await expect(page.getByRole('button', { name: 'Excel', exact: true })).toBeVisible();
```

#### 6.6 Prerequisite: Login + navigation

Before any MRT E2E test, the app must be authenticated and the table page
must be loaded. See the
[`playwright-e2e-spa-auth-navigation`](../playwright-e2e-spa-auth-navigation/SKILL.md)
base skill for fixture setup, login flow, and navigation strategy.

## Composition by Higher-Level Skills

Distribution-unit-specific composer skills can defer to this base skill's
Step 4 (fix `enable*` prop), Step 5 (verify with playwright-cli) and Step 6
(Playwright E2E test patterns) while adding repo-specific table file paths,
page routes, and verification wrappers. The composer's
`## Composition Rationale` describes the exact deferral per section.

## Related skills

- [`playwright-e2e-spa-auth-navigation`](../playwright-e2e-spa-auth-navigation/SKILL.md) — Base skill for
  Playwright E2E fixture setup, login, navigation, and headless mode patterns
- [`table-persistence-implementation`](../table-persistence-implementation/SKILL.md) — for
  `useTablePersistence` hook and localStorage persistence patterns
- [`playwright-cli`](https://github.com/microsoft/playwright-cli/tree/main/skills/playwright-cli) — browser
  automation for verifying UI fixes
- [`gitignored-reference-detection`](../gitignored-reference-detection/SKILL.md) — detect and remediate
  references to gitignored files (playwright-cli SKILL.md is gitignored locally; this base skill documents
  the public-URL substitution pattern)
- [`scripts/find-mrt-config-issues.py`](scripts/find-mrt-config-issues.py) — automated cross-file enable* prop scanner
