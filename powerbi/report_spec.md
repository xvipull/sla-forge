# SLAForge Power BI report specification

This specification is the implementation contract for the Power BI report. The semantic model should connect to `data/sla_forge.db` (or the governed SQL views in production) and use single-direction relationships from dimensions to facts.

## Model and field roles

| Table | Role | Relationship |
| --- | --- | --- |
| `dim_date` | Mark as the Date table using `calendar_date`; hide `date_key` from report authors. | `dim_date[date_key]` → `fact_ticket_sla[created_date_key]` (active); resolved date relationship inactive. |
| `dim_priority`, `dim_category`, `dim_queue` | Slicer and grouping dimensions; hide surrogate keys. | One-to-many to `fact_ticket_sla`; queue also one-to-many to `fact_assignment`. |
| `fact_ticket_sla` | One row per ticket; measures use this grain. | Ticket-level SLA, elapsed time, backlog, and risk. |
| `fact_assignment` | One row per ownership event. | Use only for handoff diagnostics; do not join it directly into ticket-count visuals. |
| `v_breach_risk_decision_support` | Detail/drill-through source. | One row per ticket and model run. |

## Core DAX measures

```DAX
Tickets = COUNTROWS ( fact_ticket_sla )
SLA Attainment % = 1 - DIVIDE ( SUM ( fact_ticket_sla[sla_breached] ), [Tickets] )
MTTA (hrs) = AVERAGE ( fact_ticket_sla[mtta_hours] )
MTTR (hrs) = AVERAGE ( fact_ticket_sla[mttr_hours] )
Reopen Rate % = AVERAGE ( fact_ticket_sla[reopened] )
Avg Transfers = AVERAGE ( fact_ticket_sla[transfer_count] )
FCR % = DIVIDE ( CALCULATE ( [Tickets], fact_ticket_sla[transfer_count] = 0, fact_ticket_sla[reopened] = 0 ), [Tickets] )
72h+ Backlog = CALCULATE ( [Tickets], fact_ticket_sla[state] IN { "OPEN", "PENDING" }, fact_ticket_sla[age_hours] >= 72 )
SLA Attainment Prior Month = CALCULATE ( [SLA Attainment %], DATEADD ( dim_date[calendar_date], -1, MONTH ) )
SLA Attainment MoM pp = [SLA Attainment %] - [SLA Attainment Prior Month]
SLA Target % = 0.90
SLA Target Gap pp = [SLA Attainment %] - [SLA Target %]
High Risk Open = CALCULATE ( [Tickets], fact_ticket_sla[state] IN { "OPEN", "PENDING" }, fact_ticket_sla[risk_band] = "Critical" )
```

Format rates as percentages, elapsed time as `0.0 hrs`, and target gaps as `0.0 pp`. Use conditional formatting: attainment below target red, within two percentage points amber, and at/above target green.

## Report pages

1. **Executive overview** — KPI cards for SLA attainment, MTTA, MTTR, FCR, reopen rate, and high-risk open work; monthly SLA line with target; queue attainment bar; “last refreshed” card and target definitions. Slicers: created date, priority, initial queue, category.
2. **Queue diagnostics** — matrix of queue × SLA, MTTR, transfers, reopen rate, aged backlog, and risk; scatter of average transfers versus SLA attainment sized by ticket count; tooltip page with ticket count, top category, and target gap. Drill-through target: queue.
3. **Trend and cohorts** — monthly SLA and ticket volume combo chart, month-over-month percentage-point KPI, priority cohort small multiples, and category breach-rate decomposition. Use the date table for all time intelligence.
4. **Ticket detail** — drill-through page filtered by `ticket_id`; show lifecycle timestamps, targets, SLA flags, queue/category/priority, transfer count, model probability/band, baseline band, and top driver explanation. Include a back button and “not an employee score” note.
5. **Data quality** — refresh timestamp, source/staging/fact row counts, null rates, freshness age versus 168-hour threshold, reconciliation differences, and blocking check status from `reports/data_quality_report.json`.
6. **Definitions and help** — KPI definition table, clock limitation, slicer instructions, model/baseline explanation, data owner, refresh cadence, privacy notes, and report contact.

## Interaction and governance

- Add page-level tooltip reports for queue and ticket visuals; keep tooltip fields limited to the decision context.
- Configure `ticket_id` as the drill-through field and retain all slicer filters when drilling.
- Add bookmarks for “Executive” and “At-risk open work” views; do not hide filters needed to reproduce a result.
- Use object-level security or workspace roles to restrict production ticket detail; the prototype contains synthetic data only.
- Show `run_as_of` and source freshness on every page. Do not publish a green status when a blocking quality check fails.
