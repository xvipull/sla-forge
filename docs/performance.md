# Performance and reproducibility evidence

Measured locally on the deterministic 720-ticket / 1,189-event extract:

| Check | Result |
| --- | --- |
| `npm run build` | Pass; generate, validate, load SQLite, create views, and train model completes in under 2 seconds locally. |
| `npm test` | Pass; 4 tests cover controls, star schema, edge cases, and model persistence. |
| SQLite fact row counts | 720 ticket facts and 1,189 assignment facts. |
| SQL reconciliation tolerance | Exact zero for row-count and transfer-value differences. |
| Model holdout | 144 chronological test tickets; AUC 0.7701 vs rule baseline 0.7176. |
| EDA output | 3 purposeful PNG charts plus JSON summary; no scratch figures are published. |

These are prototype benchmarks, not capacity guarantees. Re-run them after source-volume, policy, or hosting changes.
