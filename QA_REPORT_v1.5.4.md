# Homeflow v1.5.4 — QA report

Date: 2026-10-29

This update adds explanatory text and native expandable help. No financial formulas, saved-data structures or user amounts changed.

Validation:

- All 14 existing package checks passed.
- JavaScript syntax checks for `app.js` and `sw.js`, and `git diff --check`, passed.
- Calculation wording was reviewed against the actual forecast and allocation code, including the combined figure's exclusion of new savings.
- Browser checks confirmed three help panels, Greek/English wording, keyboard activation, descriptive accessible labels, and mobile expansion at 320 × 760 without page overflow.
- Both light and dark themes were inspected; no browser console errors were recorded.

The calculation engine was unchanged. The broader calculation/transaction suites were not rerun for this text-only update. Physical-device installation and offline upgrades were not tested.
