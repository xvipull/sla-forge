# Project charter — Enterprise Service Desk SLA & Root-Cause Analytics

## Purpose

SLAForge is an internal analytics product that turns service-desk ticket and assignment-history data into a trusted view of SLA performance, work aging, and recurring operational failure modes. It helps service leaders intervene before customer commitments are missed and directs improvement effort toward the queues, services, and handoff patterns that create avoidable delay.

## Business problem

Service performance is spread across operational reports that emphasize ticket volume rather than the end-to-end customer commitment. Leaders cannot reliably reconcile SLA results, distinguish one-off incidents from systemic bottlenecks, or identify whether poor attainment is driven by intake, assignment, response, resolution, rework, or aging backlog. This delays intervention and makes improvement priorities subjective.

## Stakeholder personas

| Persona | Goals and pain points | Decisions enabled |
| --- | --- | --- |
| IT Service Manager | Owns SLA performance and service reporting; needs one governed answer rather than manual reconciliation. | Which breached or at-risk tickets need escalation; whether SLA targets are being met by priority, service, and queue. |
| Operations Director | Accountable for customer experience, capacity, and cross-team service health. | Where to shift capacity, sponsor problem management, or change operating policy; whether performance trends justify investment. |
| Support Lead | Runs a support queue and coaches analysts; needs actionable diagnostics rather than a score alone. | Which backlog cohort to work first; which handoff, reopen, and ownership patterns to reduce; which recurring issues warrant root-cause review. |

## Decisions the product must support

1. Prioritize open tickets most likely to miss their committed response or resolution target.
2. Locate SLA underperformance by queue, priority, service, channel, and time period.
3. Separate demand growth from process failure by examining aging, transfers, reopens, and first-contact resolution.
4. Identify recurring categories or services for problem-management and root-cause investigation.
5. Track whether operational interventions improve customer-facing outcomes over time.

## Scope

### In scope

- Incident and service-request ticket extracts, including lifecycle timestamps, priority, service, channel, state, and SLA-policy attributes.
- Assignment-history events used to measure ownership intervals, transfer count, and queue handoffs.
- Governed ticket-grain SLA mart, queue scorecards, KPI definitions, data-quality checks, and decision-ready reporting.
- Explainable breach-risk triage for open work; it assists prioritization and does not make automated decisions.
- Daily refresh processing and a Power BI/Excel-ready curated data contract.

### Out of scope

- Writing to, closing, routing, or otherwise changing tickets in the ITSM platform.
- Employee performance rankings, disciplinary use, or automated staffing decisions.
- Natural-language analysis of ticket bodies, attachments, call recordings, or customer sentiment in the initial release.
- Production-grade predictive modelling, real-time streaming, and business-calendar/pause-clock calculations in the prototype.
- Replacing the ITSM system of record or its official contractual SLA reports.

## Delivery and governance

| Area | Definition |
| --- | --- |
| Product owner | IT Service Manager |
| Executive sponsor | Operations Director |
| Primary data owner | Service Operations, accountable for ticket and assignment-history extract completeness |
| Data stewards | ITSM Platform Owner (source semantics); Service Reporting Lead (KPI sign-off) |
| Technical owner | Analytics Engineering |
| Refresh cadence | Daily by 08:00 local time for the prior completed day; month-end results are frozen after validation |
| Reporting grain | One row per ticket in the curated SLA mart; assignment history remains event-grain |
| Initial delivery | Governed datasets, SQL transformations, documentation, and operational dashboard/report templates |

## Assumptions, risks, and mitigations

| Item | Impact | Mitigation / owner |
| --- | --- | --- |
| SLA policy and pause rules vary by service or contract. | Incorrect breach classification. | Document policy precedence; validate a representative ticket sample with Service Reporting Lead. |
| Assignment history can have missing or overlapping events. | Transfers and ownership duration may be biased. | Run completeness, sequence, and overlap checks; flag exceptions for ITSM Platform Owner. |
| Ticket timestamps may use inconsistent time zones. | Aging and SLA intervals can be wrong. | Normalize to UTC in staging and display a documented reporting time zone. |
| Backfilled or reopened tickets change historical results. | Trend reports may restate. | Track extract timestamp and publish a restatement note with monthly releases. |
| Users may treat risk score as a performance judgement. | Inappropriate employee-management use. | Show feature-level explanation, restrict use to work triage, and include dashboard guidance. |
| Source access or refresh fails. | Stale decisions. | Surface data-as-of timestamp and alert the data owner when daily checks fail. |

## Security and privacy

- The prototype stores deterministic synthetic data only. Production data must be classified according to the enterprise data-handling policy before onboarding.
- Use least-privilege, read-only source access; restrict curated datasets and reports to authorized Service Operations and leadership roles.
- Exclude ticket descriptions, requester names, email addresses, phone numbers, attachments, credentials, and other direct identifiers from the initial analytics mart.
- Use approved encrypted storage and transport; retain raw extracts only for the agreed operational retention period, then purge according to policy.
- Risk indicators are operational triage aids. They must not be used as the sole basis for decisions about individuals.

## Measurable acceptance criteria

| # | Criterion | Evidence of acceptance |
| --- | --- | --- |
| 1 | Curated ticket count reconciles to the accepted source ticket population for each refresh, with documented exclusions. | Automated reconciliation output shows zero unexplained variance. |
| 2 | Required fields, ticket-key uniqueness, timestamp ordering, and assignment-history referential integrity are checked on every refresh. | Data-quality report is produced and all blocking controls pass. |
| 3 | SLA attainment, MTTA, MTTR, reopen rate, transfer count, backlog aging, and first-contact resolution each have an approved formula, numerator, denominator, grain, and owner. | KPI catalog is reviewed and signed off by Service Reporting Lead. |
| 4 | An IT Service Manager can identify the highest-risk open ticket and its contributing factors in under five minutes. | UAT scenario completed successfully. |
| 5 | An Operations Director can identify the lowest-attaining queue and compare it with transfer, reopen, and aging indicators for a selected period. | UAT scenario completed successfully. |
| 6 | A Support Lead can filter a queue backlog into actionable aging cohorts and locate recurring handoff/reopen patterns. | UAT scenario completed successfully. |
| 7 | All published outputs display a data-as-of timestamp, reporting period, and the prototype clock limitation. | Dashboard/report review confirms required labels. |
