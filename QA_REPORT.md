# Homeflow v1.1.1 — verification report

## Scope

This is a user-facing wording update, based on the complete v1.1.0 package.
29 Greek/English text pairs were revised. No new financial assumptions or
features were introduced. References to private prefilled amounts, development
decisions and publication steps were removed from the visitor interface.
Practical instructions, data-loss confirmations, incomplete-month warnings,
sharing consent and the limits of the calculations are retained.

## Executed checks on this release

| Suite | Passing groups / assertions |
| --- | ---: |
| Calculation engine (`node tests/engine.test.js`) | 40 |
| Presets and atomic batch edits (`node tests/presets.test.js`) | 30 |
| Package / static service-worker checks (`node tests/package.test.js`) | 14 |
| Existing browser regression suite (`python tests/browser.test.py`) | 63 |
| Guided-entry usability (`python tests/usability.test.py`) | 57 |
| Actual standalone HTML smoke checks (`python tests/offline.test.py <HTML>`) | 12 |
| New Greek/English copy regression (`python tests/copy.test.py`) | 42 |

All the suites above were rerun for v1.1.1. JavaScript syntax checks also passed.

The new copy suite checks the empty welcome, all five sections in Greek and
English, the example confirmation and label, sharing consent, the generated
link destination, import instructions and privacy notices. It verifies the
removed messages do not exist in runtime source or tested visible text.

Existing UI suites cover expense shortcuts, arbitrary descriptions and custom
categories, decimal comma/point, quick monthly setup, duplicate warnings,
actual transactions, CSV import, JSON backup, sharing and the support panel.
Responsive checks ran at 320, 390, 768 and 1440 px in Chromium.
The new welcome screenshots were visually inspected at 390 and 1440 px.

## Compatibility and preservation

A comparison against the v1.1.0 ZIP verified that `app.js` differs only inside
bilingual text calls: after replacing their literal text with markers, both
files are identical. Thus UI control flow, calculations and stored values were
not modified.

Byte-for-byte comparisons also confirmed these remain unchanged:

- `engine.js`, `presets.js` and `styles.css`.
- `manifest.webmanifest` and its project-relative scope.
- The blank Excel template and both donation QR assets.

The storage key is still `homeflow:budget:v1` and the budget JSON schema is still
version 1. The offline asset cache is now `homeflow-static-v1.1.1`. Cache cleanup
remains restricted to this app; saved budgets are not cleared by the update.

## Test limitations

Browser suites used Playwright/Chromium with inline local assets and an
in-memory Storage adapter. The standalone smoke test loaded the actual
standalone HTML in a storage-denied context. These are not proof of real-device
persistence or an end-to-end PWA update.

Hosted deployment, real browser restarts, native Android/iPhone installation,
Safari/WebKit, OS clipboard/share permissions and live service-worker updates
were not tested. No repository was changed and no donation or payment was made.
The supplied ZIP is a release package for manual replacement of the website
files.

## Before updating the public app

Keep a private JSON backup from the existing app. Replace the site files in the
same repository directory, retain the current Pages settings, and check the
footer shows v1.1.1 after deployment. Do not clear browser data. Confirm your
saved entries remain available. Keep personal backups outside the public repo.
