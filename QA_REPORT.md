# Homeflow v1.4.0 — verification report

## Scope

This release adds investment-return projections, optional existing invested capital, per-budget-entry notes, missing-expense suggestions, and a stronger Household control. It preserves the Homeflow v1 storage key and schema version so existing browser data can migrate through validation defaults.

## Automated checks

A total of **347 automated checks / test groups** passed across the calculation engine, preset catalogue, ordering, copy/navigation, row colouring, scoped-entry UI, general browser behaviour, usability flows, offline standalone build, QR byte integrity, packaging, and new v1.4 flows.

Key v1.4-specific checks include:

- legacy saved budgets receive `investmentStart = 0`, `investmentReturn = 7`, and empty notes without reset;
- investment growth is compounded separately from available cash;
- 0% investment return equals starting invested balance plus contributions;
- notes survive validation and are scrubbed by anonymised sharing;
- Notes column saves inline edits;
- new expense suggestions exclude already-recognised budget items;
- default investment return is 7% and is editable;
- the future view shows projected investment value and modelled gain/loss;
- the Wealth Goal Planner link carries existing invested balance, monthly contribution and assumed return;
- mobile Plan view remains within the viewport;
- the Household button is visually distinct;
- both user-supplied QR PNG files remain byte-exact in the package and standalone build.

## Calculation model for investments

Investment return is an **assumption, not a forecast**. The app converts the annual effective return into a monthly factor and applies it to the separate investment balance, then adds that month’s investment contribution. Household available cash is not increased by investment gains. The projection does not model taxes, investment fees, volatility, or sequence-of-returns risk.

## Test environment / limits

UI tests used headless Chromium with simulated viewport sizes including 320, 390, 768 and 1440 CSS pixels. Touch behaviour is simulated where covered by the existing suite. The live GitHub Pages deployment and persistence/install behaviour on a physical Android or iPhone were **not** tested in this environment.

Before replacing a live deployment, keep a private JSON backup of the current browser data.
