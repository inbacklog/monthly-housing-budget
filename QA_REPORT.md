# Homeflow v1.2.0 — QA and compatibility report

## Release scope

Built from the complete v1.1.1 package in this conversation. Changes are row
ordering and ease of entry, not a new financial model. No repository or live
website has been modified.

### Added and verified

- Dedicated left-hand drag handles in Budget and Actuals. Mouse and emulated
  touchscreen moves, drop indicator, drag ghost, edge autoscroll and cancellation.
- Tap-to-position dialog plus ArrowUp/ArrowDown/Home/End keyboard alternatives.
  Focus follows a keyboard move. Undo restores the previous order.
- Filtered moves reorder only visible slots: hidden rows, amounts, IDs,
  descriptions, categories, funding, person assignment and pause flags remain
  intact. Sorting actuals does not change dates or completed-month flags.
- Actual transaction order can be customized per month; Date ↓ restores date
  ordering. Other months' stored records are not moved by a filtered move.
- Persistent + Add entry button with Budget/Actuals context and four types.
  Add-entry buttons also appear at the end of each list.
- Entry type first, followed by amount and matching description suggestions.
  Income does not show expense suggestions. Type changes preserve the amount,
  person and date; description/category drafts return when switching back.
- Decimal comma in inline list editing as well as entry and batch forms.
- Nonmodal quick-add and donation panels do not overlap. The fixed buttons stay
  separate on small screens. No automatic price, income or expense is inserted.

## Automated results

| Suite | Passed named checks / groups |
| --- | ---: |
| Calculation engine (`node tests/engine.test.js`) | 40 |
| Presets and batch edits (`node tests/presets.test.js`) | 30 |
| Row-order data invariants (`node tests/order.test.js`) | 17 |
| Packaging and static service-worker checks (`node tests/package.test.js`) | 14 |
| Existing browser flows (`python tests/browser.test.py`) | 63 |
| Guided-entry usability (`python tests/usability.test.py`) | 57 |
| Greek/English copy regression (`python tests/copy.test.py`) | 42 |
| New ordering/quick-add/type-first interactions (`python tests/interactions.test.py`) | 68 |
| Actual standalone HTML (`python tests/offline.test.py <HTML>`) | 12 |
| **Total** | **343** |

A named check/group may include several assertions or randomized invariants;
343 is not a claim of 343 separate devices or browser configurations. All suites
passed. JavaScript syntax checks passed for the shipped source. A final rerun
of interactions and the built offline HTML also passed after tightening the
Undo/storage-failure feedback.

Responsive checks cover widths 320, 390, 768 and 1440 px, Greek and English,
light/dark UI, compact menus and input dialogs. Screenshots of the actual
rendered desktop table, mobile form and dark quick-add menu were inspected.

Pointer tests used Chromium CDP `Input.dispatchTouchEvent` to exercise real
emulated touch events, including interrupted gestures. This is stronger than
calling a sorting function directly, but it is still not a physical-phone test.

## Compatibility and data protection

- `homeflow:budget:v1` is retained. There is no `localStorage.clear()` or reset.
- JSON schema stays at version 1 with an optional `actualManualMonths` array.
  Old backups without it are accepted and default to date ordering for actuals.
- Budget order lives in the existing `lines` array. Custom actual order lives in
  `transactions`, with the month flag deciding whether to apply date sorting.
- JSON backup/restore and new shared snapshots preserve the order. Excluding
  actuals from sharing also removes their ordering metadata.
- Previously saved amounts and categories remain valid. The financial formulas
  were not changed. Tests compare totals/forecasts before and after sorting.
- The suggestion catalogue, manifest, all three templates and both donation QR
  images match v1.1.1 byte-for-byte. No personal workbook or filled budget is
  included in the public package.
- Cache version is `homeflow-static-v1.2.0`; cleanup is still restricted to the
  Homeflow cache prefix. This does not clear saved budgets or other apps' caches.

## Important test limits

The environment blocked HTTP browser navigation, including localhost. Browser
suites therefore used inline local assets and an in-memory Storage adapter.
Reloading the app with that adapter verifies serialization/readback and order
preservation, not persistence after a real browser or OS restart. The standalone
smoke test used the actual generated HTML in a storage-denied context.

No live GitHub Pages deployment, real service-worker upgrade, Safari/WebKit,
physical Android/iPhone, screen-reader audit, native OS clipboard/share dialog,
real-browser restart, donation or payment was tested. No WCAG conformance claim
is made. Pointer cancellation, keyboard alternatives and tap-to-position were
implemented and tested for practical accessibility.

Technical references used for implementation:
- https://developer.mozilla.org/en-US/docs/Web/API/Pointer_events
- https://developer.mozilla.org/en-US/docs/Web/API/Element/setPointerCapture
- https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html

## Updating

Download a private JSON backup first. Replace matching website files in the
same repository root, keeping the current Pages path and settings. Do not clear
browser site data. After deployment, reload and check for v1.2.0 in the footer.
Verify a drag, a saved order after reopening, a new income and a new expense on
an actual phone. Keep personal JSON/CSV/Excel files out of the public repository.
