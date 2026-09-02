# Data dictionary

Timestamps are stored in ISO 8601 / UTC in staging and curated layers. Source-system identifiers are treated as opaque business keys. Field additions and semantic changes require approval from the relevant data steward.

## `data/raw/tickets.csv` — source extract, one row per ticket

| Field | Type | Required | Definition / validation |
| --- | --- | --- | --- |
| `ticket_id` | string | Yes | Unique ticket business key; non-null and unique within extract. |
| `created_at` | timestamp | Yes | Time the ticket entered the service desk; must precede later lifecycle timestamps. |
| `first_response_at` | timestamp | No | First qualifying analyst response; null allowed for unresponded open work. |
| `resolved_at` | timestamp | No | Resolution timestamp; null for unresolved work. |
| `priority` | string | Yes | Governed urgency/impact tier used to select SLA policy. |
| `category` | string | Yes | Standardized issue classification for root-cause grouping. |
| `initial_queue` | string | Yes | First operational queue assigned to the ticket. |
| `state` | string | Yes | Current lifecycle state; allowed values governed by ITSM platform owner. |
| `reopened` | boolean | Yes | Whether the ticket was reopened at least once. |
| `response_target_hours` | decimal | Yes | Applicable response commitment in hours; must be positive. |
| `resolution_target_hours` | decimal | Yes | Applicable resolution commitment in hours; must be positive. |

## `data/raw/assignment_history.csv` — source extract, one row per ownership event

| Field | Type | Required | Definition / validation |
| --- | --- | --- | --- |
| `ticket_id` | string | Yes | Foreign key to `tickets.ticket_id`. |
| `sequence` | integer | Yes | Chronological event sequence per ticket; positive and unique per ticket. |
| `queue` | string | Yes | Queue that owned the ticket during the interval. |
| `assigned_at` | timestamp | Yes | Start of queue ownership interval. |
| `unassigned_at` | timestamp | No | End of interval; null allowed for current owner. |

## Curated datasets

| Dataset / field | Type | Meaning |
| --- | --- | --- |
| `ticket_sla_mart.ticket_id` | string | Curated ticket-grain business key. |
| `ticket_sla_mart.response_breached` | boolean | True when governed response elapsed time exceeds response target. |
| `ticket_sla_mart.resolution_breached` | boolean | True when governed resolution elapsed time exceeds resolution target. |
| `ticket_sla_mart.sla_breached` | boolean | True when either governed breach flag is true. |
| `ticket_sla_mart.mtta_hours` | decimal | Created-to-first-response calendar hours. |
| `ticket_sla_mart.mttr_hours` | decimal | Created-to-resolution calendar hours; null until resolved. |
| `ticket_sla_mart.transfer_count` | integer | Number of assignment events minus one, minimum zero. |
| `ticket_sla_mart.age_hours` | decimal | Created-to-resolution or created-to-as-of elapsed hours. |
| `ticket_sla_mart.risk_score` | decimal | Explainable 0–99 priority index for open-ticket triage. |
| `ticket_sla_mart.risk_band` | string | Operational triage label: Stable, Watch, or Critical. |
| `queue_scorecards.queue` | string | Reporting queue identifier. |
| `queue_scorecards.sla` | decimal | Queue-level percentage of SLA-attaining tickets. |
| `queue_scorecards.transfers` | decimal | Mean transfer count for the queue. |
| `queue_scorecards.risk` | decimal | Mean ticket risk score for the queue. |
