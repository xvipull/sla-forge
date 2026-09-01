-- MySQL 8 reporting layer. Ticket grain is one ticket; assignment history is event grain.
WITH assignment_counts AS (
  SELECT ticket_id, COUNT(*) - 1 AS transfer_count
  FROM assignment_history GROUP BY ticket_id
), ticket_sla AS (
  SELECT t.ticket_id, t.initial_queue, t.priority, t.reopened,
    TIMESTAMPDIFF(HOUR, t.created_at, t.first_response_at) AS mtta_hours,
    TIMESTAMPDIFF(HOUR, t.created_at, COALESCE(t.resolved_at, CURRENT_TIMESTAMP)) AS mttr_hours,
    CASE WHEN TIMESTAMPDIFF(HOUR,t.created_at,t.first_response_at) > t.response_target_hours
           OR TIMESTAMPDIFF(HOUR,t.created_at,COALESCE(t.resolved_at,CURRENT_TIMESTAMP)) > t.resolution_target_hours
         THEN 1 ELSE 0 END AS sla_breached,
    COALESCE(a.transfer_count,0) AS transfer_count
  FROM tickets t LEFT JOIN assignment_counts a USING (ticket_id)
)
SELECT initial_queue, COUNT(*) AS tickets,
  ROUND(100 * AVG(1-sla_breached), 1) AS sla_attainment,
  ROUND(AVG(mttr_hours), 1) AS mttr_hours,
  ROUND(AVG(transfer_count), 1) AS avg_transfers
FROM ticket_sla GROUP BY initial_queue ORDER BY sla_attainment;
