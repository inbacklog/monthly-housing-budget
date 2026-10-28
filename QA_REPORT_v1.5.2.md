# Homeflow v1.5.2 — QA report

Date: 2026-10-29

## Changes checked

- Independent recovery of budget data and display preferences at startup.
- Selective reopening of completed months during CSV imports.
- Budget result counts, filtered-empty messaging, and Clear filters in Greek and English.
- Version footer and service-worker cache updated to v1.5.2.

## Automated verification

All 116 checks/groups passed:

| Command | Passed |
| --- | ---: |
| `node tests/engine.test.js` | 50 |
| `node tests/startup.test.js` | 10 |
| `node tests/presets.test.js` | 30 |
| `node tests/reorder.test.js` | 12 |
| `node tests/package.test.js` | 14 |

JavaScript syntax checks passed for `app.js`, `engine.js`, `presets.js`, and `sw.js`.

Startup cases cover malformed JSON, null/array/primitive preferences, preference read errors, valid preferences, malformed budget data, unavailable budget storage, and a first visit. CSV cases cover plan-only imports, actual imports touching multiple months, and atomic rejection of an invalid import.

## Browser verification

Checked the real app through a localhost HTTP server in the in-app browser using fictional demo data:

- All 14 demo budget entries are shown initially.
- A search with no matches shows 0 of 14 and the correct empty-state message.
- Clear filters restores all 14 entries and keyboard focus to search.
- Combining category, type, and Greek text search returns the single expected electricity entry.
- Switching to English updates the count and empty-state wording.
- Dark theme and a 390 × 844 viewport retain usable filter controls; no page-level horizontal overflow was detected.
- No browser console errors were recorded during these checks.

## Limits

The older Python/Playwright browser suites were not run in this Windows environment. No physical iPhone/Android installation or offline upgrade from an existing device cache was tested. The package checks verify cache versioning and asset references; browser checks used the new version directly.
