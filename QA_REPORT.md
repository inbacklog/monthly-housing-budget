# Homeflow v1.0.0 — Verification report

## Executed

**40 calculation-engine test groups**, including 100 deterministic allocation invariant cases:

- Each recurring frequency and one-offs; 14-pay income averaging.
- Paused lines; members do not multiply amounts.
- Cash versus benefit versus mixed income.
- Saving/investment separation and no double-counting in allocations.
- Deficit preservation, extra-saving cap and nonnegative extra investment.
- Monthly actuals isolation and incomplete-month flags.
- Forecast accumulation, growth, one-offs and 10% discretionary scenario.
- Date validation, malformed inputs, duplicate IDs and prohibited funding combinations.
- CSV quoting, BOM, delimiter/decimal variants, atomic validation, named members.
- Default share anonymization and formula-like CSV export sanitization.
- Safe dictionary keys for arbitrary custom categories.

**63 Chromium interface checks**, covering:

- Empty public start, voluntary labelled demo, English/Greek and dark theme.
- Multi-person creation/removal without changing totals.
- Free amount entry, custom category, literal user HTML, inline edits and pause.
- Search and subscription filters.
- Actual expense-only use, month navigation, completeness and edit invalidation.
- Horizon settings and safe Wealth Goal Planner handoff.
- Compact non-modal support card, QR image loading, Lightning link, Escape close.
- Sharing consent, default redaction and compressed encode/decode roundtrip.
- Invalid CSV safety, import preview, duplicate warnings and JSON replacement.
- No page-level horizontal overflow across **320, 390, 768 and 1440 px**, on each of the five sections.
- No uncaught JavaScript exceptions in these flows.

**12 package/static service-worker checks:** local assets, manifest paths, template presence/parse, no personal workbook in package, isolated storage/cache prefixes, excluded cross-origin and other-project paths, sharing disclosure.

**2 QR payload checks:** generated Buy Me a Coffee and Lightning QR images decoded independently to their intended URL/address. No payment was made or wallet transaction tested.

The Excel template was inspected and rendered; key ranges have no formula-error cells. It is an input template and intentionally contains no financial calculation formulas.

## Test-environment limitations

Browser navigation to HTTP/HTTPS and file URLs is blocked in this execution environment. UI checks therefore loaded inlined HTML/CSS/JavaScript using Playwright `set_content`. An in-memory Storage adapter was used for persistence-flow checks. This verifies application logic, **not actual cross-restart browser persistence**.

The standalone app was also rendered in a storage-denied context; calculations still work and the UI warns that data is not being saved.

The service-worker checks are package/unit checks, **not an end-to-end online-to-offline installation test**. Hosted GitHub Pages deployment, real-device Android/iOS installation, actual browser cache eviction, real clipboard permissions and native share sheets still need device/deployment checks.

No Safari/WebKit engine, bank connection, tax validation, external provider subscription cancellation, or financial payment is claimed to have been tested.

## Before sharing the live URL

1. Upload the package and confirm successful GitHub Pages deployment.
2. On a real phone, enter fictional data, reload and verify persistence.
3. Create a share link and open it in another browser; verify the explicit adoption flow.
4. Download JSON, restore it and confirm the same entries/settings.
5. After a successful online load, test offline reopening and home-screen installation.
6. Verify external donation links open the correct service; do not use a test payment unless personally intended.

Do not publish any filled workbook or financial backup while testing.
