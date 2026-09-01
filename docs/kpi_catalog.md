# KPI catalog

| KPI | Definition | Target |
| --- | --- | --- |
| SLA attainment | Tickets without response or resolution breach / all tickets | >= 90% |
| MTTA | Mean created-to-first-response calendar hours | < 4 hrs |
| MTTR | Mean created-to-resolution (or as-of) calendar hours | < 36 hrs |
| Reopen rate | Reopened tickets / all tickets | < 10% |
| First-contact resolution | No transfer and not reopened / all tickets | >= 65% |
| Transfer count | Assignment history events minus one | Minimize |
| Backlog aging | Unresolved tickets grouped by elapsed age | 72h+ = attention |

The breach-risk index is an explainable triage score, not a prediction or automated decision. It weights elapsed time against SLA target, transfer count, reopen state and infrastructure queue context.
