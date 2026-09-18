# Homeflow 1.1.0 — quicker expense entry


A local-first, bilingual (Greek / English) household budget app for **one person or a larger household**. Mobile-friendly. Static HTML/CSS/JavaScript; no npm, build server, account, API key or database required.

**Intended Pages URL:** https://inbacklog.github.io/monthly-housing-budget/

## New expense-entry workflow

In **My budget** and **Actuals**, visible shortcuts include Groceries, Rent, Electricity,
Water, Internet, Fuel, Pharmacy and Streaming. The **All expenses** picker contains
61 expense descriptions, searchable in Greek/English, with editable categories.
There are also 9 income/saving/investment labels in the detailed entry form.
No suggested price or household amount is inserted. Selecting a label does not
replace the amount, frequency, date or person already entered. Default
essential/subscription flags are suggestions and can be changed.

**Quick monthly setup** groups current expense entries and blank suggestions by
category. Enter only relevant amounts, choose a period and review the monthly
sum. Empty new rows and new zero rows are not added. An existing zero is a
valid explicit update; clearing an existing amount leaves it unchanged.
Existing record IDs, people, funding sources, paused flags and one-off months
are preserved. Batch edits require review and an acknowledgement before save.
The existing recurring-budget-across-months model is unchanged.

**Save & add another** records the entry once and opens a blank amount/description
for the next. Possible duplicates require acknowledgement; differently worded
bills may still escape detection, so do not count a category total and the same
underlying expenses. Category tiles are computed summaries, not extra budget rows.

## Updating an existing installation

1. In the current app, use **Files & templates → JSON backup**; keep it private.
2. Replace the website files with all files from this package in the same repo root.
3. Keep the same repository, Pages path and storage. Do not clear browser site data.
4. Commit the files and reopen/reload the published site after deployment.
5. Check the footer says **v1.1.0**. The JSON schema and local-storage key are unchanged.

The package is complete, not a patch. No live repository was modified by creating it.

## Start

Upload this folder's **contents** (not the ZIP, not an extra parent directory) to the `main` branch of `inbacklog/monthly-housing-budget`. `index.html` must be at the repository root. Choose **Settings → Pages → Deploy from a branch → main → / (root)**.

Official instructions: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

The repository is not modified by preparing this package. Publication and real-device installation need a deployment check.

## Main features

- Empty public start; deliberately fictional demo behind a confirmation.
- Add/remove household members; optional names; shared or assigned entries. Members never multiply amounts automatically. Technical safeguard: up to 1,000 members, 10,000 planned entries and 10,000 transactions.
- Budget income, living expenses, saving transfers and investment transfers separately.
- Monthly, annual, quarterly, weekly, 14-paycheck salary and one-off entries. Pause and edit entries, flag subscriptions/essential expenses, add custom categories.
- Net cash income, restricted benefits and unsplit mixed income handled separately. Vouchers are not silently counted as cash available to invest.
- Actual transactions by month, including expense-only use. No invented income or automatic budget + actual double count.
- Mark a month complete to unlock category variances. Editing actuals reopens completeness. A completed actual month can become a new budget with explicit replacement confirmation.
- Donut category breakdown, income-to-remainder explanation, member assignment summaries and data-based observations.
- Configurable reserve target, extra savings and a user-chosen percentage of the remaining surplus for additional investment. Default extra investment percentage is zero.
- 1–120 month projections, income/expense growth assumptions, annualized cash model, 10% lower discretionary-spending and 10% lower-income comparisons, monthly table and CSV export.
- Optional handoff to Wealth Goal Planner of the monthly investment contribution only. No personal capital is assumed.
- CSV upload with validation, preview, confirmation and duplicate-looking-row warning. JSON full backup/restore.
- Shareable compressed URL snapshots; editable independent copies. No synchronized shared accounts.
- Light/dark theme, guide, keyboard-labelled controls, local-only auto-saving, scoped offline support, optional PWA installation.
- Small bottom-right coffee panel with Buy Me a Coffee and Bitcoin Lightning address, QR codes and copy action.

## Important financial distinctions

**Budget, not a bank statement.** Annual and weekly expenses are averaged across months. Fourteen salaries are averaged over twelve months. A projected positive balance does not establish that cash is available on each bill's actual due date.

Cash flow uses:

```
net cash income
− cash living expenses
− planned saving transfers
− planned investment transfers
− additional saving target (capped at available surplus)
− user-selected share of the remaining surplus for extra investment
= unassigned cash flow (negative values are retained)
```

There is one recurring budget shared across months; editing it recalculates prior budget comparisons. Keep JSON snapshots for historical budget versions. Actual transactions remain dated and separate. Opening available cash is the balance at the start of the selected forecast month and is not rolled forward automatically from earlier actuals.

Opening available cash excludes the emergency reserve; otherwise the same balance would be counted twice. Existing reserve does not earn modelled returns and is not silently consumed in projections.

The monthly reserve target = user-chosen months × marked essential monthly expenses. The default 3 months is an editable illustrative setting, not personal advice. If no essential expenses are marked, the app warns against interpreting a zero target as no need for savings.

Forecasts use planned entries, **not** an extrapolation of partial actuals. Annual changes compound gradually month by month. One-off amounts are not repeated or grown. There are no investment returns, probability estimates or tax/loan calculations beyond entered amounts. Scheduled transfers remain visible even if a budget cannot fund them; warnings flag underfunded months and negative cash.

Restricted-benefit income and corresponding benefit-funded expenses are separate from cash totals. Mixed income awaits explicit splitting and is excluded from cash. Cash and benefit amounts must not be duplicated.

## Import / export

See `templates/`. The workbook is a convenient **entry template**, not a general XLSX importer. Save `Plan_CSV` or `Actual_CSV` as CSV UTF-8 before import. Arbitrary Excel, PDF and bank-statement import is intentionally unsupported: silently guessing their meaning would be unsafe.

CSV header, in this order:

```
kind,date,type,description,category,amount,frequency,member,essential,subscription,funding
```

- `kind`: `plan` or `actual`.
- `date`: ISO `YYYY-MM-DD` for actual; `YYYY-MM` for one-off planned entries; otherwise blank.
- `type`: `income`, `expense`, `saving`, `investment`.
- `amount`: nonnegative; up to 2 decimal places; no currency sign or thousands separators.
- `frequency`: `monthly`, `yearly`, `quarterly`, `weekly`, `salary14` (income only), `once`. Blank for actual.
- `member`: optional exact name; unknown nonempty names create members; blank means shared.
- `essential`, `subscription`: `true` or `false`; only planned expense flags affect the model.
- `funding`: `cash`, `benefit`, `mixed` (income only). Saving/investment transfers must use cash.
- Standard category codes are listed in the template and `engine.js`. Custom nonempty text is supported.
- Comma-delimited CSV with decimal point, or semicolon-delimited CSV with decimal comma. UTF-8 BOM and quoted fields are supported.

Imports are validated entirely before applying. CSV **appends**; duplicate-looking rows are warned, not silently deduplicated. CSV exports only active planned entries and actual transactions; it is **not** a full backup of settings, paused rows, or completeness. Use JSON for full fidelity. JSON replacement requires preview confirmation. Maximum input size: 2 MB.

Formula-like CSV text is prefixed to reduce spreadsheet formula-injection risk. Descriptions are displayed as escaped text, not HTML.

## Sharing and privacy

Inputs stay in this browser under `homeflow:budget:v1`. Theme/language use `homeflow:prefs:v1`. No analytics, trackers, ads, remote calculation calls or bank credentials. Data is not encrypted at rest.

Links carry a snapshot after `#plan=`. The fragment is not part of the HTTP request, **but anyone with the link can decode it**. Browser history and messaging apps can retain it. Compression is not encryption. There is no link revocation, live synchronization or collaborative editing.

Names/descriptions are removed by default; actual transactions are excluded by default. Amounts, categories and household structure remain. The user must consent before creating a link. The recipient sees a pending-copy banner and must confirm before replacing an existing local budget. Large snapshots use JSON rather than unreliable giant URLs.

**Never upload a filled personal workbook, CSV or JSON backup into the public repository.** Only the empty/fictional templates are included here.

GitHub Pages projects for the same owner share an origin; separate storage keys are not a security boundary against all same-origin apps. Normal hosting logs and third-party support-service processing are outside this app's control.

## Offline / device installation

`sw.js` caches only this app's assets in `homeflow-static-*` and controls only this project path. Other apps' caches are not deleted. First successful online caching is required. Browser eviction or clearing storage removes offline data. The Excel template is included in this version’s asset cache after a successful online installation. Dynamically generated CSV templates work offline.

The separate standalone HTML has scripts, styles, icons, QR images and Excel template embedded and does not register a service worker. File-opening behavior on smartphones varies; the published HTTPS URL is the intended mobile experience.

## Tests

```
node tests/engine.test.js
node tests/presets.test.js
node tests/package.test.js
python tests/browser.test.py
python tests/usability.test.py
python tools/build_offline.py /path/to/Homeflow_Offline.html
python tests/offline.test.py /path/to/Homeflow_Offline.html
```

The browser suite uses Playwright and Chromium, not required for end users. Read `QA_REPORT.md` for executed checks and limits. Financial formulas live independently in `engine.js`. UI and translations are in `app.js`; no external JavaScript libraries are loaded.

## Background information

- CFPB emergency-fund and cash-flow guide: https://www.consumerfinance.gov/an-essential-guide-to-building-an-emergency-fund/
- CFPB income, benefits and spending toolkit: https://www.consumerfinance.gov/consumer-tools/educator-tools/your-money-your-goals/toolkit/
- GitHub Pages: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

These are general educational references, not Greek tax rules, individualized recommendations, or endorsements of the app.
