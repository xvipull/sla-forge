# SLAForge

**Enterprise Service Desk SLA & Root-Cause Analytics**

SLAForge is a portfolio-grade service operations product for IT Service Managers, Operations Directors and Support Leads. It turns ticket events and assignment history into governed SLA metrics, queue handoff diagnostics, an explainable breach-risk queue and a responsive executive command center.

## Business questions

- Where and why are service levels failing?
- Which queues create excess rework or transfers?
- Which open tickets should leaders intervene on first?
- How is aging backlog affecting customer experience?

## Architecture

```text
Synthetic tickets + SLA policy + assignment history
                 ↓
validation, event reconstruction and SLA-clock logic
                 ↓
curated ticket SLA mart + queue scorecards
                 ↓
SQL reporting views + explainable risk score
                 ↓
interactive command center / Power BI-ready data
```

## Quick start

```bash
npm run build
npm test
cd web && python3 -m http.server 8080
```

Open `http://localhost:8080`. The deployed dashboard uses deterministic, synthetic data only.

## KPI governance

The reporting grain is one service desk ticket. Assignment history is reconstructed into transfer counts; elapsed calendar hours are used for the demo SLA clock. Core KPIs are SLA attainment, MTTA, MTTR, reopen rate, transfer count, backlog aging and first-contact resolution. Source-to-curated ticket counts reconcile to zero difference.

See [requirements](docs/requirements.md), [KPI catalog](docs/kpi_catalog.md), [data dictionary](docs/data_dictionary.md), [assumptions](docs/assumptions.md) and [UAT](docs/uat.md).

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
