# Homeflow v1.2.0 — validation report

## Executed checks

| Suite | Passed | Failed | Scope |
|---|---:|---:|---|
| `tests/engine.test.js` | 58 | 0 | Existing calculation, input, import and sharing regression tests |
| `tests/scenarios.test.js` | 29 | 0 | Independent documents, workspace validation, comparison and sharing |
| `tests/browser.test.py` | 91 | 0 | Existing Chromium UI regression tests with explicitly simulated localStorage |
| `tests/scenarios.browser.test.py` | 57 | 0 | Onboarding, comparison, independent editing, migration and shared-copy UI |
| `tests/package.test.js` | 19 | 0 | Asset completeness, namespaces and isolated simulated service-worker policy |
| Standalone release smoke checks | 11 | 0 | Bundled HTML, embedded assets/template, guide and three-scenario comparison |

265 checks passed. These are test cases, not a security certification or a
promise that the software is defect-free. UI smoke checks use fictional data.

## Scenarios and calculation boundaries

The original plan counts as one of at most three independent documents. Tested:
minimum/maximum count, independent cloned plans/settings/members/goals, optional
actual transaction copying, reference versus active selection, delete behavior,
name escaping/length checks, strict workspace schemas, serialisation, anonymising
all scenario names, complete JSON restore and compatibility with legacy single
budget documents/links.

Comparisons use the same selected month and 1–120 month horizon. Per-scenario
income and flexible-expense changes and extra monthly costs affect BOTH the
first-month summary and the forecast. Actual transactions are not silently used
as planned values. Alternatives are not added together. The shared chart plots
cumulative projected remainder starting from zero, not bank balance, wealth or
investment returns. No success probability or investment recommendation is made.

Unknown/review-needed values and underfunded vouchers withhold capacity/deltas.
Empty plans are not presented as confirmed zero budgets. Deficits remain visible;
extra investment capacity is never negative. The scenarios model was tested
against independent expected totals, differing months, recurring/one-off entries,
annual changes, nulls, missing data, refunds, and unchanged source documents.

The existing household engine regression checks cover frequency normalisation,
14 payments/year, timing bounds, pausing, savings/investment separation, user
cushion, restricted benefits, partial actuals, goal allocations, household cost
allocation, CSV parsing/escaping, XLSX and legacy mapping, and share protection.

## User experience and persistence

The skippable first-run guide has three routes: plan a month, record actuals only,
or import a file. Money fields start blank. The guided plan has input and review
steps and is not saved before confirmation. Amounts are household totals, not
multiplied by member count. Aggregate living costs are flagged for review with a
warning against adding both aggregate and detailed expenses.

Three desktop comparison cards, a compact three-column mobile summary, independent
edit controls, reference deltas and the shared chart were checked. Phone detail
cards stack below the simultaneous summary. Both languages/themes were exercised.
Comparison overflow checks passed at 320, 390, 768, 1024 and 1440 pixels. Existing
screens were also checked at 320, 360, 390, 768 and 1440 pixels. Desktop and phone
screenshots were visually inspected. Long tables intentionally use internal
horizontal scrolling. Real-transaction quick-add is hidden on guide/comparison
screens, where it would be distracting; the compact coffee panel remains.

Workspace saves use one storage write. Tested with simulated storage: serialised
workspace restoration, visibly reported quota failures, preserving legacy storage,
corrupted workspace protection, and cross-tab conflict safeguards. Full JSON
backup/restore covers all scenarios. Shared editing cannot silently replace the
recipient's local workspace. Accepting/importing a whole workspace requires
explicit replace-all confirmation. Local storage/backups are unencrypted.

Share defaults exclude actuals and strip descriptions and names (including scenario
names). Optional password protection uses the existing Web Crypto implementation;
round trips, wrong passwords and tampered ciphertext were tested, not independently
security-audited. Raw share payloads are capped at 2 MB to match the decoder;
the UI prevents unwieldy URLs above 8,000 characters and recommends private JSON.
There is no simultaneous remote collaborative editing or account backend.

## Public package and standalone

The package includes only application files, generic templates, documentation and
tests. The original personal workbook and any filled inputs are NOT distributed.
Public text was scanned for the original people's names and prior personal
scenario-specific example amounts, with no matches. The optional example is
fictional and marked as such. Existing support destinations are unchanged; no
payment, wallet or account was accessed.

`scenarios.js` is loaded in the correct dependency order and included in the scoped
v1.2.0 PWA cache. The standalone HTML inlines scripts/styles and needed image assets,
embeds the generic Excel template and does not register a service worker. The
standalone release rendered the guide and three-scenario chart without external
script/style requests. Both embedded QR images loaded; no real wallet payment or
phone-scanner behavior was tested for this release.

## Important untested boundaries

Ordinary loopback browser navigation was blocked in this runner. Browser tests
therefore used **Playwright `page.set_content` with embedded local resources and
an explicitly simulated in-memory storage Map**. The standalone smoke check used
the same local content-rendering approach. The shipped application contains no
test-storage shim.

Do NOT interpret this report as verification of deployed GitHub Pages, real-origin
browser persistence across restarts, cross-device behavior, a complete
service-worker install/update lifecycle, iPhone Safari or a physical mobile install.
Cache tests are isolated policy simulations, not live offline lifecycle tests.

## Deployment acceptance checklist

1. Back up any existing local budget to private JSON before updating site files.
2. Publish all files, including the new `scenarios.js`; confirm footer v1.2.0.
3. On the actual HTTPS origin, enter fictional inputs, duplicate twice, edit each,
   reload/restart the browser and check all three remain independent.
4. Export all-scenario JSON, restore in a second browser and verify totals/reference.
5. Open an anonymous all-scenario link in that browser, edit it, then discard it:
   the recipient's local workspace must remain unchanged. Test explicit acceptance.
6. Test password-protected links with correct/incorrect passwords and practical URL
   length in the messaging service used. Exchange passwords separately.
7. Test local-storage conflict warnings across two real tabs. Download backup before
   reloading if a conflict or save failure occurs.
8. Install on real Android/iOS, load online, reopen offline, and verify the version
   update flow. Re-test CSV/XLSX imports and QR scanning in target browsers.

No repository write or live deployment was performed. No bank-account reconciliation,
tax/legal review, penetration test, formal accessibility audit or cryptographic
security audit is claimed.
