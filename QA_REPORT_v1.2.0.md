# Homeflow v1.2.0 — verification report

## Release scope

- One prominent, contextual `+ Add entry` button at the top of Budget and Actuals.
  It sticks within its list card. There is no global floating add button and no
  add launcher on Overview, What's next or Guide.
- The entry form begins with the income/expense type and amount, before
  description suggestions. Income selection offers income suggestions.
- Drag by the left handle to reorder budget entries or the selected month's
  actual transactions. Mouse and touch pointer paths are implemented.
- Tap a handle for an exact position, or use Up/Down/Home/End on a focused handle.
- Filtering reorders only the visible slots. Hidden rows, other months, amounts,
  identifiers and dates are retained. Actual-month completion flags are not
  changed by an order-only update.
- Reordering restores the table's scroll offsets instead of resetting its scroll.
- Removed duplicate generic add buttons from the list empty states/shortcut area.
- Corrected new control theme variables and checked light/dark views.

## Executed on this release

| Suite | Passing groups / assertions |
| --- | ---: |
| Financial calculation engine (`node tests/engine.test.js`) | 40 |
| Presets / atomic batch edits (`node tests/presets.test.js`) | 30 |
| Package / static service worker (`node tests/package.test.js`) | 14 |
| New ordering engine (`node tests/reorder.test.js`) | 12 |
| Existing browser regression (`python tests/browser.test.py`) | 63 |
| Guided-entry usability (`python tests/usability.test.py`) | 57 |
| Bilingual visitor-copy regression (`python tests/copy.test.py`) | 42 |
| New scoped-entry / order UI (`python tests/context-order.test.py`) | 39 |
| Actual standalone HTML (`python tests/offline.test.py <HTML>`) | 12 |

JavaScript syntax checks passed. New ordering checks exercise actual mouse
pointer capture, Chromium touch events through DevTools, keyboard ordering,
numeric position selection, cancellation, visible-only order changes, and the
absence of the global add launcher. Tests use synthetic demo records, not a
private household workbook.

Responsive checks cover widths of 320, 390, 768 and 1440 px. The new desktop
budget list, mobile income form and dark mobile list screenshots were inspected.

## Preservation

The existing financial-engine code is unchanged: only a separate pure reorder
function and its export were added. Presets, the PWA manifest, the blank Excel
template, and both donation QR images are byte-identical to v1.1.1.

Storage remains `homeflow:budget:v1` with schema version 1. Array order is stored
in the same existing `lines` / `transactions` fields. No financial values are
migrated and no storage is cleared. The asset cache is `homeflow-static-v1.2.0`;
cleanup remains limited to Homeflow caches, not other applications.

## Test limitations

Chromium tests load inline local assets with an in-memory Storage adapter.
A full UI reload was tested with that adapter, not an actual browser restart.
The standalone test runs the packaged HTML without test instrumentation and
checks operation when storage is unavailable. Touch events were emulated;
no physical Android/iPhone, Safari/WebKit, native PWA installation, production
GitHub Pages deployment or live service-worker upgrade was tested. No payment
was made. These are application tests, not independent financial certification.

## Updating

First download a private JSON backup from the existing app. Replace the files
at the same repository root, keep your current Pages configuration, and check
that the footer says v1.2.0 after publication. Refresh normally; do not clear
browser storage. Personal JSON/CSV backups do not belong in the public repo.
