# Data pipeline and quality controls

## Flow and reproducibility

`python3 src/generate_data.py && python3 src/pipeline.py` regenerates the deterministic demo extract, preserves the raw layer, writes typed standardized staging files, loads `data/sla_forge.db`, publishes curated marts, and emits `reports/data_quality_report.json`. No external package or mutable source-system connection is required.

| Layer | Asset | Purpose and transformations |
| --- | --- | --- |
| Raw | `data/raw/tickets.csv`, `data/raw/assignment_history.csv` | Source-shaped immutable input. It is never edited by the cleaning pipeline. |
| Staging | `data/staging/stg_*.csv` and `stg_*` SQLite tables | Trim and uppercase business keys; normalize timestamps to UTC ISO 8601; cast targets to decimal, sequence to integer, and reopened to boolean; standardize controlled categories and queues. |
| Dimensional | `dim_date`, `dim_priority`, `dim_category`, `dim_queue` | Conformed dimensions with integer surrogate keys and preserved business values. |
| Fact | `fact_ticket_sla`, `fact_assignment` | Ticket-SLA fact is one row per ticket; assignment fact is one row per ownership event. Both use surrogate keys; `ticket_id` remains a durable business key. |
| Curated | `ticket_sla_mart.csv`, `queue_scorecards.csv` | Governed SLA metrics and operational scorecards for reporting. |

## Automated controls

| Control | Rule | Failure behavior |
| --- | --- | --- |
| Required columns | Both raw extracts must have the documented schema. | Stops the build. |
| Null thresholds | Ticket ID, created time, first response, assignment ticket ID, and assignment start are 0%; `resolved_at` is at most 15%. | Stops the build. |
| Duplicates | `ticket_id` must be unique; `(ticket_id, sequence)` must be unique in history. | Stops the build. |
| Keys and values | Ticket IDs match `INC-#####`; priorities, state, category, queue, and booleans are standardized/validated. | Stops the build. |
| Ranges and dates | SLA targets are positive; response/resolution are not before creation; assignment end is not before start. | Stops the build. |
| Referential integrity | Every assignment references a staged ticket and every ticket has ownership history. SQLite foreign keys are enforced. | Stops the build. |
| Freshness | Latest ticket creation must be within 168 hours of the configured reporting as-of timestamp. | Stops the build. |
| Reconciliation | Raw-to-staging and staging-to-fact row differences must be zero; total transfers must equal assignment events minus tickets. | Stops the build. |

The generated JSON report records source counts, threshold results, freshness, database counts, and reconciliation outcomes. Blocking failures raise `DataQualityError` and do not publish a successful report.

## Transformation rules

1. Preserve `tickets.csv` and `assignment_history.csv` as source-shaped raw inputs; the pipeline never updates them.
2. Trim whitespace and uppercase `ticket_id`, priority, and state. Ticket IDs must match `INC-#####`.
3. Parse all lifecycle and ownership timestamps, assume UTC only when a source offset is absent, and write UTC ISO 8601 timestamps to staging.
4. Cast SLA targets to decimal hours, assignment sequence to integer, and `reopened` to a boolean from `true`, `1`, or `yes`.
5. Map case-insensitive category and queue values to governed display values. Unmapped values fail rather than silently becoming null.
6. Reject nonpositive targets, out-of-order ticket or assignment timestamps, missing resolution time on a resolved ticket, duplicate keys, and orphan ownership events.
7. Derive `mtta_hours`, `mttr_hours`, age, response/resolution/headline breach flags, transfer count, risk score, and risk band only after staging validation.
8. Generate date, priority, category, and queue dimensions; load ticket and assignment facts with their surrogate-key relationships; then aggregate reporting marts.
