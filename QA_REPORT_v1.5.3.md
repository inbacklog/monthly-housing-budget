# Homeflow v1.5.3 — QA report

Date: 2026-10-29

## Scope

Record actual from a budget row, undo the last deleted entry, and return to the current month. No changes to financial formulas or the saved-data schema.

## Automated checks

All 136 checks/groups passed:

| Suite | Passed |
| --- | ---: |
| `node tests/engine.test.js` | 50 |
| `node tests/startup.test.js` | 10 |
| `node tests/shortcuts.test.js` | 20 |
| `node tests/presets.test.js` | 30 |
| `node tests/reorder.test.js` | 12 |
| `node tests/package.test.js` | 14 |

The shortcut suite executes the real app handlers with controlled UI/storage boundaries and the real calculation engine. It covers all six payment frequencies, every financial type, funding and notes, unchanged source records, deletion order, single-use undo, completion flags, valid/invalid later edits, navigation and focus fallback.

JavaScript syntax checks and `git diff --check` passed.

## Browser checks

Verified through a localhost HTTP preview in the in-app browser with fictional demo entries:

- Current month returns from another month and is disabled when already selected.
- A yearly insurance entry opens with its full €360 amount, today's date in the current month, and the original description/category.
- Cancelling retains all 14 planned entries. Saving opens Actuals with a new transaction and keeps the plan unchanged.
- Repeating the same payment displays the duplicate warning and prevents an unacknowledged save.
- Deleting an actual reopens its completed month. Undo after navigating to another month restores the transaction and its original completion flag without moving the selected month.
- Deleting a budget entry offers Undo; changing language preserves and translates the notice.
- A draft in September defaults to September 1; Save & add another opens blank amount/description fields.
- At 320 × 760 the page has no horizontal overflow and the undo notice remains readable with usable Undo/Dismiss buttons. Budget tables retain their own horizontal scrolling.
- No console errors were recorded.

## Limits

The Python/Playwright suites and physical-device PWA installation were not run. Undo is held only in memory and intentionally ends after a later data edit, reload, dismissal or another deletion. Legacy amounts with more than two decimal places must be corrected to cents in the new actual form, consistent with its existing amount validation.
