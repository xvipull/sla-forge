-- SQLite KPI semantic layer. Views retain ticket grain until their stated aggregation.
DROP VIEW IF EXISTS v_ticket_kpi;
CREATE VIEW v_ticket_kpi AS
SELECT f.ticket_key, f.ticket_id, f.created_at, d.year_month AS created_month, p.priority_code AS priority,
       c.category_name AS category, q.queue_name AS initial_queue, f.state, f.reopened,
       f.mtta_hours, f.mttr_hours, f.age_hours, f.sla_breached, f.transfer_count,
       f.risk_score, f.risk_band
FROM fact_ticket_sla f
JOIN dim_date d ON d.date_key=f.created_date_key
JOIN dim_priority p ON p.priority_key=f.priority_key
JOIN dim_category c ON c.category_key=f.category_key
JOIN dim_queue q ON q.queue_key=f.initial_queue_key;

DROP VIEW IF EXISTS v_queue_kpi;
CREATE VIEW v_queue_kpi AS
SELECT initial_queue, COUNT(*) AS ticket_count,
       ROUND(100.0*AVG(1-sla_breached),1) AS sla_attainment_pct,
       ROUND(AVG(mtta_hours),2) AS mtta_hours, ROUND(AVG(mttr_hours),2) AS mttr_hours,
       ROUND(100.0*AVG(reopened),1) AS reopen_rate_pct,
       ROUND(AVG(transfer_count),2) AS avg_transfer_count,
       SUM(CASE WHEN state IN ('OPEN','PENDING') AND age_hours>=72 THEN 1 ELSE 0 END) AS aged_backlog_72h,
       ROUND(AVG(risk_score),1) AS avg_risk_score
FROM v_ticket_kpi GROUP BY initial_queue;

DROP VIEW IF EXISTS v_monthly_sla_trend;
CREATE VIEW v_monthly_sla_trend AS
WITH monthly AS (
  SELECT created_month, COUNT(*) AS ticket_count, ROUND(100.0*AVG(1-sla_breached),1) AS sla_attainment_pct,
         ROUND(AVG(mttr_hours),2) AS mttr_hours
  FROM v_ticket_kpi GROUP BY created_month
), lagged AS (
  SELECT *, LAG(sla_attainment_pct) OVER (ORDER BY created_month) AS prior_sla_attainment_pct,
         LAG(ticket_count) OVER (ORDER BY created_month) AS prior_ticket_count
  FROM monthly
)
SELECT *, ROUND(sla_attainment_pct-prior_sla_attainment_pct,1) AS sla_pp_change,
       ROUND(100.0*(ticket_count-prior_ticket_count)/NULLIF(prior_ticket_count,0),1) AS volume_pct_change
FROM lagged;

DROP VIEW IF EXISTS v_resolution_cohort;
CREATE VIEW v_resolution_cohort AS
SELECT created_month, priority, COUNT(*) AS ticket_count,
       ROUND(100.0*AVG(1-sla_breached),1) AS sla_attainment_pct,
       ROUND(AVG(mttr_hours),2) AS avg_mttr_hours
FROM v_ticket_kpi GROUP BY created_month, priority;

DROP VIEW IF EXISTS v_category_driver;
CREATE VIEW v_category_driver AS
SELECT category, COUNT(*) AS ticket_count, ROUND(100.0*AVG(sla_breached),1) AS breach_rate_pct,
       ROUND(AVG(transfer_count),2) AS avg_transfer_count, ROUND(100.0*AVG(reopened),1) AS reopen_rate_pct,
       ROUND(AVG(mttr_hours),2) AS avg_mttr_hours
FROM v_ticket_kpi GROUP BY category;

DROP VIEW IF EXISTS v_ticket_exception;
CREATE VIEW v_ticket_exception AS
SELECT ticket_id, initial_queue, priority, category, state, age_hours, risk_score, risk_band,
       CASE WHEN sla_breached=1 THEN 'SLA breach'
            WHEN risk_score>=70 THEN 'High breach risk'
            WHEN state IN ('OPEN','PENDING') AND age_hours>=72 THEN 'Aged backlog'
       END AS exception_reason
FROM v_ticket_kpi
WHERE sla_breached=1 OR risk_score>=70 OR (state IN ('OPEN','PENDING') AND age_hours>=72);
