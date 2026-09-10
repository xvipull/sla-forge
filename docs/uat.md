# User acceptance testing

## Entry criteria

Run `npm run build`, confirm `reports/data_quality_report.json` is `PASS`, and confirm the report/database as-of timestamp is visible. UAT uses synthetic data and is not contractual sign-off for production SLA reporting.

## Stakeholder test cases

| ID | Persona | Steps | Expected result | Status |
| --- | --- | --- | --- | --- |
| UAT-01 | IT Service Manager | Open Executive Overview; record SLA attainment, target, and data-as-of timestamp. | KPI card matches governed SLA attainment, target is 90%, and timestamp is visible. | Pass — automated build + visual review |
| UAT-02 | IT Service Manager | Open exceptions; select the highest-risk ticket and drill to detail. | Ticket ID, queue, priority, reason, transfer count, and model drivers are visible; no employee-score language. | Pass — workbook/Power BI specification |
| UAT-03 | Operations Director | Filter Queue Diagnostics to a period and compare queues by SLA and volume. | Ticket count, SLA, transfers, reopens, and aged backlog compare together under the selected filters. | Pass — SQL views + workbook |
| UAT-04 | Operations Director | Open Trend and Cohorts; compare the current month with prior month. | Month-over-month SLA percentage-point and volume changes use the date table and window logic. | Pass — `v_monthly_sla_trend` |
| UAT-05 | Support Lead | Filter a queue to open/pending work and review 72h+ aging. | Aging cohort is visible, high-risk work is prioritized, and exception action follows the scenario threshold. | Pass — workbook scenario controls |
| UAT-06 | Support Lead | Compare category breach rates and average handoffs. | Category view highlights breach, reopen, transfer, and MTTR drivers without duplicating tickets by handoff. | Pass — `v_category_driver` |
| UAT-07 | Data owner | Open Data Quality; inspect counts, nulls, freshness, and reconciliation. | All blocking controls show PASS; source-to-staging and staging-to-fact differences are zero. | Pass — generated report |
| UAT-08 | Report owner | Change workbook SLA target and critical-risk threshold. | Target gap and exception action labels update; source facts and governed counts do not change. | Pass — workbook validation |

## Edge-case and regression evidence

Automated tests cover duplicate ticket keys, invalid priority values, orphan assignments, invalid assignment intervals, null thresholds, timestamp normalization, dimensional foreign keys, model persistence, and rule-baseline comparison. Run `npm test`; the release suite passes 4 tests.

## Demo script

1. Run `npm run build` and point out the successful data-quality report and as-of timestamp.
2. Open the dashboard overview and compare SLA attainment with the 90% target.
3. Move to Queue Diagnostics; identify the lowest-attaining queue and compare transfers, reopens, and risk.
4. Open Trend and Cohorts to explain the latest month-over-month movement.
5. Drill into the top exception; explain its breach/risk reason and model driver direction.
6. Change the scenario threshold in Excel to show how the exception action changes.
7. Close with calendar-hour, synthetic-data, and human-review limitations.
