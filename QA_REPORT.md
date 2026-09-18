# Homeflow v1.3.0 — verification report

## Change

This release adds optional, type-aware row colouring to Budget and Actuals.

- Income: soft green.
- Expense: soft coral.
- Saving: soft blue.
- Investment: soft violet.
- Display modes: **Soft**, **Scale by amount**, **No colour**.
- Scale by amount compares each row only with the average amount of the same type. Budget values use monthly equivalents; Actuals compare transactions in the selected month.
- Text type labels remain visible, so colour is never the only indicator.
- The display preference is browser-local and is not encoded into shared financial links.

## Compatibility

Budget schema and local-storage key are unchanged. Row order, calculations, exports, sharing payloads and drag-and-drop behaviour are unchanged.

The supplied Buy Me a Coffee and Wallet of Satoshi QR image files are retained byte-for-byte as the packaged assets.

## Automated verification

The existing calculation, presets, ordering, package, browser-flow, copy, usability, QR and offline smoke suites were run together with a new colour-specific Chromium suite. Across those suites, **327 checks/test groups passed**. The colour suite additionally verified:

- different tints for income and expense;
- stronger tint for a higher same-type amount;
- browser persistence of the display preference;
- no-colour mode;
- dark-theme compatibility;
- mobile width at 390 px;
- no uncaught script errors.

## Limits

Automated UI checks use Chromium in this environment. No physical iPhone/Android device, Safari/WebKit installation or production GitHub Pages deployment was tested.
