# Homeflow v1.1.0 — verification report

This report describes checks actually run on the final v1.1.0 files.

## Executed in the authoring environment

| Suite | Passed |
| --- | ---: |
| Original calculation-engine test groups | 40 |
| New preset / atomic-batch test groups | 30 |
| Original UI regression assertions (Chromium) | 63 |
| New guided-entry / usability assertions (Chromium) | 57 |
| Package / static service-worker assertions | 14 |
| Actual standalone-HTML smoke assertions | 12 |

The original calculation engine is unchanged. Its existing tests include 100
deterministic allocation-invariant cases inside the reported groups.

### New data and calculation coverage

- No prices or household personal data in the suggestion catalogue.
- 61 expense descriptions and 9 income/saving/investment descriptions; unique IDs.
- Greek accent/case normalization, English search, provider search aliases and category filters.
- Legacy bilingual labels recognised without duplicating matching quick-entry suggestions.
- Decimal comma and decimal point; zero versus blank; invalid and oversized inputs.
- Atomic multi-entry creation and updates, with no mutation of the source on errors.
- Existing IDs, people, funding, flags, paused rows and one-off dates preserved.
- Blank/zero new rows skipped; existing zero updates, blank existing amount unchanged.
- Existing custom categories and higher-precision imported values preserved.
- Income, savings, investment, actual transactions and complete-month flags untouched by budget batches.
- Updated data still validates under JSON schema 1 and works with the existing CSV format.

### New UI coverage

- Visible shortcuts in Budget and Actuals; no suggested price inserted.
- Changing a suggestion retains the entered amount, person, frequency and actual date.
- Empty amounts rejected; arbitrary descriptions and user-chosen amounts accepted.
- Possible duplicate warning, no save until acknowledged, intentional overrides allowed.
- Save & add another records once and opens a blank amount/description.
- Catalogue search and subscriptions; search Enter does not submit a financial entry.
- Category summaries and filtering; no separate category-total charges added.
- Actual-only entries and full-catalogue selection stay separate from budget entries.
- Moving an actual payment reopens completion flags for both affected months.
- Batch preview, monthly conversions, review/consent gate, hidden-draft retention,
  correct existing-ID updates, cancellation and invalid-input safety.
- UI reload reads the prior v1 JSON unchanged through a storage adapter.
- Unrelated applications' storage remains untouched.
- Greek/English and light/dark rendering, compact nonmodal support panel.
- Horizontal layout checks on plan, actuals, entry dialogs and the batch editor at
  320, 390, 768 and 1440 px. Screenshots visually inspected at mobile and desktop sizes.
- No uncaught JavaScript exceptions in these tested flows.

### Package and standalone coverage

- Scripts and styles load from local files; presets load before the UI.
- All referenced assets exist; the manifest retains the same project-relative scope.
- New cache version includes presets and the blank Excel template, excludes other projects.
- Local storage key `homeflow:budget:v1` and schema 1 retained; no clear-all call.
- Private household workbook is absent; only the blank import template is included.
- Generated standalone has no external script/style dependencies or test instrumentation.
- Standalone scripts run after DOM elements exist; expense and batch entry work.
- Storage-denied warnings display instead of falsely claiming saved data.
- Embedded Excel template is byte-identical; both QR images load from embedded data.

## Limitations — not claimed as tested

Browser navigation to localhost HTTP is blocked by environment policy
(`ERR_BLOCKED_BY_ADMINISTRATOR`). UI suites therefore use Playwright `set_content`
with inline local assets. The regression suites use an in-memory Storage adapter.
This checks application behavior, not actual cross-restart browser persistence.
The standalone smoke test uses the real saved HTML, without test instrumentation,
in a storage-denied context.

Service-worker checks are package/unit checks, not an end-to-end online/offline
PWA installation test. Actual hosted deployment, cross-device sharing/navigation,
real Android/iPhone installation, native keyboard/share/clipboard permissions,
cache eviction and Safari/WebKit rendering still require device testing.
No live GitHub repository was changed and no donation/payment was made.

Duplicate detection is best-effort. It cannot know that every differently named
expense represents the same bill. The user must avoid entering both a category
total and the same itemised expenses. Preset essential/subscription flags are
editable suggestions, not personal financial guidance.

## Safe update / final live check

1. Export the existing private JSON backup in the current app.
2. Replace the website files in the same repository path. Keep Pages configuration.
3. Wait for deployment, reopen online and check the footer says v1.1.0.
4. Check your old entries/settings in the same browser. Do not clear site data.
5. Add a fictional expense, reload, verify persistence, then remove it.
6. Test a share link in a second browser and the explicit adoption flow.
7. Test offline reopening and installation on the target real phone.
8. Keep filled files and backups out of the public repository.
