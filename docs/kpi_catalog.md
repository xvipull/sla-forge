# KPI catalog

All headline measures are calculated at ticket grain and aggregated only after ticket-level validation. Unless otherwise approved, reporting includes tickets created in the selected period; open-ticket measures use a displayed as-of timestamp. Calendar hours are used in the prototype.

| KPI | Business definition and formula | Grain / segmentation | Direction & initial target | Owner |
| --- | --- | --- | --- | --- |
| SLA attainment | `(tickets without a response or resolution SLA breach ÷ SLA-eligible tickets) × 100` | Ticket; initial queue, priority, category, month | Higher; ≥90% | IT Service Manager |
| Response SLA attainment | `(tickets first responded within target ÷ response-SLA-eligible tickets) × 100` | Ticket; priority, initial queue, category | Higher; ≥92% | Support Lead |
| Resolution SLA attainment | `(resolved tickets within resolution target ÷ resolution-SLA-eligible tickets) × 100` | Ticket; priority, initial queue, category | Higher; ≥90% | IT Service Manager |
| MTTA | Mean of `first_response_at − created_at` in hours for tickets with a recorded first response | Ticket; initial queue, priority, category | Lower; <4 hours | Support Lead |
| MTTR | Mean of `resolved_at − created_at` in hours for resolved tickets | Ticket; initial queue, priority, category | Lower; <36 hours | IT Service Manager |
| Reopen rate | `(tickets reopened at least once ÷ tickets resolved in period) × 100` | Ticket; initial queue, category | Lower; <10% | Support Lead |
| First-contact resolution | `(resolved tickets with zero transfers and no reopen ÷ resolved tickets) × 100` | Ticket; initial queue, category | Higher; ≥65% | Support Lead |
| Mean transfer count | `sum(transfer_count) ÷ tickets with assignment history` | Ticket; originating/final queue, category | Lower; minimize | Operations Director |
| Aged backlog | Count of open or pending tickets grouped as 0–24, 25–48, 49–72, and 72+ elapsed hours | Open ticket; initial queue, priority, category | Lower; 72+ requires review | Support Lead |
| Breach-risk index | Explainable 0–100 triage score using elapsed time versus target, transfer count, reopen status, and operational context | Open ticket; queue, priority | Higher = prioritize; no target | IT Service Manager |

## KPI controls and interpretation

- A ticket is SLA-breached when either governed response or resolution breach flag is true. Exempt or cancelled tickets are excluded only when a documented policy says so.
- SLA eligibility, pause rules, calendars, and policy precedence require production sign-off. The prototype assumes a continuous calendar-hour clock.
- Queue scorecards must retain both the numerator/denominator and ticket count behind any percentage to avoid misleading small-population results.
- The breach-risk index is not a probability, target, or employee score. It supports work ordering and must be interpreted with ticket context.
