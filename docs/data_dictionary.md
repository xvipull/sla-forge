# Data dictionary

| Dataset | Field | Meaning |
| --- | --- | --- |
| tickets | ticket_id | Unique business key at ticket grain. |
| tickets | created_at / first_response_at / resolved_at | SLA event timestamps. |
| tickets | response_target_hours / resolution_target_hours | Policy targets at ticket priority. |
| tickets | state / reopened | Current lifecycle condition. |
| assignment_history | ticket_id / sequence | Ordered handoff event key. |
| assignment_history | queue / assigned_at / unassigned_at | Queue ownership interval. |
| ticket_sla_mart | sla_breached / mtta_hours / mttr_hours | Curated governed measures. |
| queue_scorecards | risk / sla / transfers | Queue-level operational scorecard. |
