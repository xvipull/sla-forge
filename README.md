# SLAForge

**Enterprise Service Desk SLA & Root-Cause Analytics**

SLAForge is a governed analytics foundation for IT Service Managers, Operations Directors, and Support Leads. It turns service-desk tickets and assignment history into trusted SLA metrics, queue handoff diagnostics, aging-backlog visibility, and explainable breach-risk triage.

> **Prototype notice:** the repository contains deterministic synthetic data. It uses calendar-hour SLA clocks and is not a replacement for official contractual reporting.

## Business questions

- Where and why are service levels failing?
- Which queues create excess rework or transfers?
- Which open tickets should leaders intervene on first?
- How is aging backlog affecting customer experience?

## Architecture

```text
ITSM ticket extract       Assignment-history extract       SLA-policy reference
        │                           │                              │
        └───────────────► raw / staging validation ◄───────────────┘
                                      │
                     governed SLA-clock and handoff logic
                                      │
                curated ticket SLA mart + queue scorecards
                                      │
             SQL views ──► Power BI / Excel / operational reports
```

## Repository map

| Path | Purpose |
| --- | --- |
| `docs/` | Project charter, KPI governance, data contract, and assumptions. |
| `data/raw/` | Immutable source-shaped extracts; no direct reporting. |
| `data/staging/` | Validated, standardized, and typed intermediate data. |
| `sql/` | Reproducible transformations and reporting views. |
| `src/` | Pipeline and data-generation code. |
| `notebooks/` | Exploration only; production logic belongs in `src/` or `sql/`. |
| `powerbi/`, `excel/` | Semantic-model and workbook delivery artifacts. |
| `reports/` | Published data-quality outputs and rendered report assets. |
| `tests/` | Automated controls for data and transformation logic. |

## Screenshot placeholders

_Replace these placeholders with approved, de-identified captures as delivery assets are completed._

| View | Placeholder |
| --- | --- |
| Executive SLA overview | `reports/screenshots/01-executive-sla-overview.png` |
| Queue root-cause diagnostic | `reports/screenshots/02-queue-root-cause.png` |
| Open-ticket breach-risk triage | `reports/screenshots/03-breach-risk-triage.png` |

## Quick start

```bash
npm run build
npm test
cd web && python3 -m http.server 8080
```

Open `http://localhost:8080`. The deployed dashboard uses deterministic, synthetic data only.

## KPI governance

The reporting grain is one service desk ticket. Assignment history is reconstructed into transfer counts; elapsed calendar hours are used for the demo SLA clock. Core KPIs are SLA attainment, MTTA, MTTR, reopen rate, transfer count, backlog aging and first-contact resolution. Source-to-curated ticket counts reconcile to zero difference.

See the [project charter and requirements](docs/requirements.md), [KPI catalog](docs/kpi_catalog.md), [data dictionary](docs/data_dictionary.md), [assumptions](docs/assumptions.md), and [UAT](docs/uat.md).

## Data engineering

Run `npm run build` to generate validated staging files, the local SQLite analytics database, the dimensional model, curated marts, and a machine-readable quality report. See [pipeline controls](docs/data_pipeline.md) and the [star-model contract](docs/data_model.md).

## Key techniques

- Reproducible synthetic ticket and assignment-event generation
- Required-column, duplicate and referential-integrity quality controls
- Assignment-history reconstruction and SLA-clock calculations
- Governed ticket and queue marts plus MySQL reporting views
- Explainable breach-risk triage based on handoffs, reopen status, queue and elapsed time
- Responsive stakeholder dashboard with executive and diagnostic views

## Limitations

This demonstration applies calendar-hour clocks and intentionally simple, explainable risk scoring. A production implementation should apply business calendars and pause rules, connect ITSM source systems, calibrate model thresholds, and enforce role-based access.

## Resume-ready impact

Built SLAForge, an end-to-end enterprise service desk SLA and root-cause analytics product using Python, SQL, data-quality controls, assignment-history reconstruction, governed KPI logic and stakeholder-facing BI reporting.
