# Architecture and data flow

```mermaid
flowchart LR
  A[ITSM ticket extract] --> R[Raw CSV layer]
  B[Assignment history extract] --> R
  P[SLA policy reference] --> R
  R --> S[Python validation and standardization]
  S --> T[Typed staging CSV + SQLite staging tables]
  T --> D[Conformed dimensions]
  T --> F[Ticket and assignment fact tables]
  F --> V[SQL KPI views, cohorts, exceptions, reconciliation]
  F --> M[Explainable breach-risk model + rule baseline]
  V --> BI[Power BI semantic model]
  V --> X[Advanced Excel companion]
  M --> BI
  M --> X
  S --> Q[Data-quality JSON report]
```

The ticket fact grain is one ticket; the assignment fact grain is one ownership event. Surrogate integer keys support durable joins while source `ticket_id` remains the business key. Raw inputs are preserved and only staging, curated, and database outputs are rebuilt.
