# Changelog

## v1.5.1

- Replaced the static projection SVGs with interactive charts.
- Exact values appear in a persistent readout and in a tooltip on hover/tap.
- Added crosshair and point markers for the selected month.
- Added keyboard exploration with Left/Right arrows and Home/End.
- Improved axis labels and tick formatting for long horizons.
- No calculation, storage-schema, or sharing-format changes.

# v1.5.1

- Projection horizon is now set in years, 1–50, default 10 years.
- Quick horizon presets: 5 / 10 / 20 / 30 years.
- Long projections show annual snapshots in-app; CSV remains month-by-month.
- Added combined cash + reserve + investment metric, clearly not full net worth.
- Existing v1 browser data remains compatible.

# v1.4.0

- Add editable investment-return assumption (default 7%) and optional existing invested balance.
- Project investment value separately from household cash, including contributions and modelled gain/loss.
- Add optional per-entry notes with an inline Notes column in My Budget.
- Prioritise common expense suggestions that are not yet present in the current budget.
- Make the Household / people button more visually prominent.
- Keep older saved Homeflow v1 budgets compatible through defaults for new fields.

# v1.3.0

- Replace both support QR assets with the owner-supplied original PNGs, byte for byte.
- Embed the same original bytes in the standalone HTML.
- Bump the static asset cache and footer to v1.3.0.
- Preserve the compact support panel, contextual add controls, ordering, calculations and saved data.

# v1.2.0

- Contextual, sticky list-level add control; no global entry floating button.
- Type and amount are first in the entry form; context-aware suggestions.
- Mouse/touch row reordering, keyboard controls and exact-position alternative.
- Order persistence uses the existing schema, including JSON and share export.
- Filtered ordering preserves hidden entries and other transaction months.
- Reordering preserves amounts/dates and restores table scroll offsets.
- Removed redundant list add actions and corrected dark/light style tokens.
- Added ordering and entry-context regression tests; refreshed offline cache.

# Homeflow 1.1.1

- Refined 29 bilingual UI text pairs in the welcome, example, entry guidance, files, sharing and privacy screens.
- Removed development-context wording and deployment instructions from the visitor interface.
- Kept practical guidance, data-loss confirmations, incomplete-month warnings, sharing consent and privacy limitations.
- The example now uses a simple sample-data label and explicitly warns that loading it replaces budget entries and actual transactions.
- Retained the exact calculation engine, suggestion catalogue, styles, templates, donation assets and saved-data schema.
- Bumped only the release/cache metadata to 1.1.1; no local-storage clearing or migration.
- Added bilingual copy regression checks and rebuilt the standalone HTML.

---

# Homeflow 1.1.0

## New
- Eight prominent expense shortcuts in both Budget and Actuals.
- 61 common household expense descriptions plus 9 income/saving/investing labels.
- Searchable bilingual catalogue, category filtering and free custom descriptions.
- Suggested labels inside each entry form; previous descriptions can be reused without copying prices.
- Quick monthly setup: edit existing expense rows and fill blank common expenses in one view.
- Batch review and confirmation; blank new rows are skipped, existing IDs and flags retained.
- Monthly-equivalent previews and derived category totals (not extra charges).
- Save & add another; decimal comma or point in guided amount inputs.
- Best-effort duplicate warnings with an explicit override for genuinely separate entries.

## Fixes and compatibility
- Moving a real transaction to a different month reopens both affected complete-month flags.
- Local storage key `homeflow:budget:v1`, JSON schema 1 and share links are unchanged.
- Existing data is read without being replaced by example values.
- Paused/benefit-funded/member-assigned rows are not silently changed by quick setup.
- Cached app version is bumped and the new preset module is precached.
- The optional standalone builder inlines scripts after the DOM and includes the Excel template.

## Unchanged
Calculation engine, no bank connection, public blank starting state, local-first storage,
independent shared snapshots, full JSON backup, CSV import and compact donation panel.

Preset essential/subscription flags are editable suggestions, not personalised advice.
Duplicate detection cannot infer that every differently named expense is the same bill.
