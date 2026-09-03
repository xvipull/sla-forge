# Analytics data model

## Grain and key strategy

| Table | Grain | Surrogate key | Business key / relationships |
| --- | --- | --- | --- |
| `dim_date` | One calendar date | `date_key` (`YYYYMMDD`) | Used by created and resolved dates. |
| `dim_priority` | One SLA priority | `priority_key` | `priority_code` is unique. |
| `dim_category` | One normalized issue category | `category_key` | `category_name` is unique. |
| `dim_queue` | One normalized operational queue | `queue_key` | `queue_name` is unique. |
| `fact_ticket_sla` | One row per service-desk ticket | `ticket_key` | `ticket_id` is the unique source business key; joins to date, priority, category, and initial queue. |
| `fact_assignment` | One row per ticket ownership event | `assignment_key` | `(ticket_key, event_sequence)` is unique; joins to ticket and queue. |

`fact_ticket_sla` holds additive ticket counts and semi-additive measures such as elapsed hours, breach flags, transfer count, and risk score. Queue scorecards aggregate from the ticket fact. Assignment analysis should use `fact_assignment` to prevent ticket metrics from being duplicated across handoffs.
