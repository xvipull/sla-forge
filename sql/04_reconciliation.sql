-- Reconciliation controls. All `difference` values have a documented tolerance of zero.
WITH counts AS (
  SELECT 'raw/staging tickets' AS control, (SELECT COUNT(*) FROM stg_tickets) AS source_total,
         (SELECT COUNT(*) FROM fact_ticket_sla) AS reporting_total
  UNION ALL SELECT 'raw/staging assignments', (SELECT COUNT(*) FROM stg_assignment_history),
         (SELECT COUNT(*) FROM fact_assignment)
  UNION ALL SELECT 'transfer value',
         (SELECT COUNT(*) - COUNT(DISTINCT ticket_id) FROM stg_assignment_history),
         (SELECT SUM(transfer_count) FROM fact_ticket_sla)
)
SELECT control, source_total, reporting_total, reporting_total-source_total AS difference,
       CASE WHEN ABS(reporting_total-source_total)<=0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM counts;

-- Ticket-level source-to-reporting key reconciliation (expect zero rows).
SELECT ticket_id FROM stg_tickets
EXCEPT
SELECT ticket_id FROM fact_ticket_sla;

-- Assignment foreign-key reconciliation (expect zero rows).
SELECT a.ticket_id, a.sequence
FROM stg_assignment_history a LEFT JOIN stg_tickets t ON t.ticket_id=a.ticket_id
WHERE t.ticket_id IS NULL;
