# Excel companion

The companion workbook is generated at `outputs/day6/sla_forge_decision_workbook.xlsx` by the repository build script. It is designed as a management handoff for users who need an editable exception list and a lightweight scenario control alongside the Power BI report.

## Refresh design

The `Tickets` table is the Power Query landing contract. In Excel Desktop, replace its connection with a Power Query query to the governed SQLite `fact_ticket_sla`/`v_breach_risk_decision_support` views, then refresh all queries and PivotTables. The workbook includes a `Definitions` tab with the source query, owner, refresh cadence, and field contract.

## Included tabs

- `Management Summary`: KPI cards, target gaps, queue summary, and the selected what-if target.
- `Queue Diagnostics`: formula-driven queue scorecard with conditional formatting.
- `Monthly Trend`: monthly SLA trend and chart-ready table.
- `Exceptions`: high-risk and breached tickets with XLOOKUP-backed driver fields.
- `Scenario Controls`: editable target and intervention assumptions with validation.
- `Data Quality`: row counts, freshness, null checks, reconciliation, and check status.
- `Definitions`: KPI formulas, model limitations, Power Query refresh notes, and ownership.
- `Tickets`: typed ticket-level governed data used by formulas and Pivot-compatible tables.

The workbook uses structured formulas, XLOOKUP for ticket lookups, bounded COUNTIFS/SUMIFS, and formula summaries rather than fragile duplicated calculated columns. Scenario controls are planning aids; they do not rewrite source facts.
