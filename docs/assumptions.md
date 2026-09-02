# Assumptions and decision log

| ID | Assumption / limitation | Rationale and consequence | Validation or exit condition | Owner |
| --- | --- | --- | --- | --- |
| A1 | Data in this repository is deterministic and synthetic. | It is safe for development and demonstration, but results do not represent production operations. | Replace only after privacy and source-access approval. | Product Owner |
| A2 | The prototype uses calendar-hour elapsed time. | It does not exclude business hours, holidays, or approved SLA pauses. | Implement approved business calendar and pause logic before contractual reporting. | Analytics Engineering |
| A3 | A ticket breaches the headline SLA when either response or resolution commitment is breached. | Provides a conservative customer-commitment measure. | Confirm against the enterprise SLA policy. | Service Reporting Lead |
| A4 | Open and pending work is measured to a fixed reporting as-of timestamp. | Enables reproducibility; results must state the timestamp. | Replace fixed cut-off with refresh runtime in production. | Analytics Engineering |
| A5 | Assignment events are sufficient to derive transfer count. | Missing or out-of-order history will understate or overstate handoffs. | Reconcile event sequence and exception rate with ITSM Platform Owner. | ITSM Platform Owner |
| A6 | `reopened` represents one or more valid post-resolution reopens. | It supports quality diagnostics but does not identify cause. | Validate field semantics and derive from event history if required. | Service Operations |
| A7 | Breach-risk scoring is transparent, rule-based triage. | It must not be represented as a prediction or used for individual performance actions. | Operational review of usefulness and bias before wider release. | IT Service Manager |
| A8 | Service, category, priority, and queue values are governed dimensions. | Unmapped values can fragment reporting. | Maintain mapping tables and report unmapped-value rate. | Data Steward |
