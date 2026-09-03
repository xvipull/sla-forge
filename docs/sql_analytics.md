# SQL analytics and reconciliation layer

[`03_kpi_views.sql`](../sql/03_kpi_views.sql) is executed whenever the SQLite database is rebuilt. It provides reusable semantic views instead of duplicating KPI calculations in reports:

| View | Grain / purpose |
| --- | --- |
| `v_ticket_kpi` | One ticket, conformed dimensions and governed ticket measures. |
| `v_queue_kpi` | One initial queue, SLA, elapsed-time, rework, transfer, risk, and aged-backlog KPIs. |
| `v_monthly_sla_trend` | One creation month, with `LAG` window functions for SLA percentage-point and volume changes. |
| `v_resolution_cohort` | One creation-month and priority cohort for service-level trend comparison. |
| `v_category_driver` | One root-cause category, exposing breach, transfer, reopen, and elapsed-time drivers. |
| `v_ticket_exception` | One ticket requiring intervention: breached, high-risk, or aged open/pending work. |

[`04_reconciliation.sql`](../sql/04_reconciliation.sql) proves raw/staging-to-fact counts and the transfer measure reconcile within the documented tolerance of zero. Its key- and foreign-key exception queries must return no rows.

Run `npm run build`, then execute the SQL files with any SQLite-compatible client against `data/sla_forge.db`. Run `npm run eda` to publish the EDA figures and `reports/eda_summary.json`.
