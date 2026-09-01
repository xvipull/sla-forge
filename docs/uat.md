# UAT checklist

| Test | Expected result | Status |
| --- | --- | --- |
| Fresh build | Generator and pipeline complete without manual input | Pass |
| Required columns | Missing required ticket fields fail validation | Pass |
| Ticket uniqueness | Duplicate ticket IDs fail validation | Pass |
| Event integrity | Every ticket has assignment history | Pass |
| Reconciliation | Raw and curated ticket counts differ by zero | Pass |
| Dashboard | KPI cards, queue risk, aging and intervention queue render | Pass |

Demo script: open the command center, compare SLA attainment against the 90% target, locate the highest-risk queue, then inspect the top ticket in the intervention queue and the 72h+ aging segment.
