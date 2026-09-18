# Homeflow 1.2.0

## New
- Pointer-event row dragging on dedicated handles, including emulated touch coverage.
- Tap-to-position alternative, keyboard movement, edge scrolling, drop indicator and Undo.
- Stored budget order; manual per-month actual order and explicit date-sort reset.
- Filtering preserves hidden record slots. Sorting preserves amounts, IDs and completed-month flags.
- Fixed + Add entry popover with Budget/Actuals context and income/expense shortcuts.
- Add-another buttons at the end of both lists.
- Type-first form buttons; amount before the description catalogue.
- Suggestions follow type; separate description drafts are restored when switching back.
- Decimal-comma support in inline budget amounts.

## Compatibility
- Keeps `homeflow:budget:v1` and version-1 JSON; adds optional `actualManualMonths`.
- Old backups are accepted; new JSON and shared links preserve row order.
- No financial calculation formula, preset, template, support address or QR changes.
- Cache version bumped to 1.2.0; no saved-data clearing.

---

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
