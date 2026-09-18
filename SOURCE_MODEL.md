# Workbook basis and explicit additions

The app uses the **structure** of the supplied household workbook. Personal names, amounts, the original workbook and private financial records are intentionally absent from this public package.

## Structure preserved

- **Budget overview:** projected and actual income, expenses and remaining balance.
- **Monthly expenses:** Description, Category, Projected cost, Actual cost, Difference, Actual cost overview.
- **Budget summary:** grouped categories and projected-versus-actual totals.
- **Additional data:** category list supporting the summary.
- The administrative solve-order sheet is not a user budgeting feature and is not reproduced.

The original category vocabulary is retained as English labels with Greek UI translations: **Children, Entertainment, Food, Gifts and charity, Housing, Insurance, Loans, Personal care, Pets, Savings, Subscriptions, Taxes, Transportation**.

The source includes a 14-pay salary convention and an extra-income description combining cash and benefits. The app supports 14-pay monthly equivalents and requires explicit cash-versus-restricted-benefit classification rather than inferring a spendable amount.

## Deliberate changes and additions (not assertions about the workbook)

- Source Savings entries were part of the expense/outflow structure. The app exposes **saving** and **investment** as separate transfer types while still deducting them once from available cash. This changes presentation, not their cash-outflow nature.
- Income, Health, Travel and Other categories are convenience additions. All categories and descriptions can be customized.
- Household members, essential flags, subscription pause, recurring frequencies and one-off months are new controls. The source does not determine household roles or which expenses a user must regard as essential.
- Actuals now require dates. The original workbook's actual amounts are not silently assigned an invented month, and are not copied into this distribution.
- Missing actuals stay incomplete until the user explicitly marks the month complete. The app does not treat missing receipts as savings.
- Projections, reserve targets, extra allocations, conditional tips, template import, independent shared links and PWA support are new app features.
- Demo numbers are fictional and voluntary. They are not derived from the user's private income/expense amounts.

The original workbook has not been edited. This is not a verified accounting/tax implementation or a general-purpose workbook converter.

## v1.1 additions (not workbook-derived financial assumptions)

The new catalogue provides common descriptions with no amounts. Quick setup groups
existing rows and blank suggested entries by category. It edits the same underlying
budget lines, not an additional set of category totals. Actuals remain separate.
The supplied workbook and any personal numbers remain excluded from this package.
