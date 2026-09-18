# Homeflow v1.5.0 — verification report

## Scope
- Projection horizon moved to years: 1–50, default 10 years.
- Quick presets: 5 / 10 / 20 / 30 years.
- Internal model remains monthly for calculations and CSV export.
- In-app projection table switches to annual snapshots above 5 years.
- Added combined financial-position metric: available cash + emergency reserve + projected investments. It is explicitly not a full net-worth calculation.
- Existing v1 local-storage budgets remain compatible.

## Automated verification
254 automated test groups/checks passed across calculation engine, packaging, QR assets, bilingual copy, v1.4 regression flows, v1.5 horizon behavior, scoped-entry UI, usability, row colouring, and drag/reordering.

Key verified cases:
- default horizon = 120 months / 10 years;
- 50-year / 600-month horizon accepted and 601 months rejected;
- 20-year view shows annual snapshots rather than 240 on-screen monthly rows;
- full CSV export remains month-by-month;
- investment return affects investment projection only, not household cash;
- old browser data format and storage key remain unchanged;
- notes, drag-and-drop, colours, contextual add controls and original supplied support QR assets continue to work.

## Test environment / limitations
- Browser UI tests: headless Chromium on desktop/mobile viewport simulations.
- Not tested on a physical iPhone/Android device or against the live GitHub Pages deployment.
- Long-term projections are deterministic scenarios based on the user's assumptions; they are not forecasts or probabilities.
