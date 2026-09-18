# Homeflow v1.5.1 — QA Report

## Scope

This update replaces the two static projection charts with explorable charts. Budget calculations, investment calculations, saved-data schema, imports, exports and shared-link format are unchanged.

## What changed

- Persistent exact-value readout below each chart.
- Tooltip with exact values on hover, pointer movement or tap.
- Crosshair and coloured markers for the selected month.
- Keyboard exploration: Left/Right month by month, Home/End first/last point, Escape closes a pinned tooltip.
- Clearer euro-formatted Y-axis labels and date ticks for long horizons.
- Both cash scenarios and investment value/contributed capital are explorable.

## Validation performed

- 297 automated test groups/checks passed across the calculation engine, presets, ordering, copy, colours, usability, packaging, QR assets and standalone build.
- A targeted Chromium interaction check confirmed that the cash and investment charts render, show exact euro values, respond to pointer movement and keyboard navigation, and keep the final-point readout visible.
- JavaScript syntax checks passed for `app.js`, `engine.js` and `presets.js`.

## Limitations

- Browser interaction was checked in local Chromium, not on every physical Android/iPhone browser.
- The charts remain deterministic illustrations based on the user's assumptions; they are not market forecasts or probabilities.
