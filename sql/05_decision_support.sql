-- Governed advanced-analytics outputs. Predictions retain one row per ticket and model run.
CREATE TABLE IF NOT EXISTS model_run (
  model_run_id TEXT PRIMARY KEY, model_name TEXT NOT NULL, trained_at TEXT NOT NULL,
  train_ticket_count INTEGER NOT NULL, test_ticket_count INTEGER NOT NULL, threshold REAL NOT NULL,
  feature_list_json TEXT NOT NULL, assumptions TEXT NOT NULL, test_auc REAL NOT NULL,
  test_precision REAL NOT NULL, test_recall REAL NOT NULL, test_accuracy REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS model_driver (
  model_run_id TEXT NOT NULL, feature_name TEXT NOT NULL, coefficient REAL NOT NULL,
  odds_ratio REAL NOT NULL, direction TEXT NOT NULL, driver_rank INTEGER NOT NULL,
  PRIMARY KEY(model_run_id, feature_name), FOREIGN KEY(model_run_id) REFERENCES model_run(model_run_id)
);
CREATE TABLE IF NOT EXISTS fact_breach_risk_prediction (
  model_run_id TEXT NOT NULL, ticket_key INTEGER NOT NULL, data_partition TEXT NOT NULL,
  actual_breach INTEGER NOT NULL, model_probability REAL NOT NULL, model_band TEXT NOT NULL,
  baseline_probability REAL NOT NULL, baseline_band TEXT NOT NULL,
  PRIMARY KEY(model_run_id, ticket_key), FOREIGN KEY(model_run_id) REFERENCES model_run(model_run_id),
  FOREIGN KEY(ticket_key) REFERENCES fact_ticket_sla(ticket_key)
);
DROP VIEW IF EXISTS v_breach_risk_decision_support;
CREATE VIEW v_breach_risk_decision_support AS
SELECT p.model_run_id, t.ticket_id, t.created_month, t.priority, t.category, t.initial_queue,
       t.state, t.transfer_count, p.data_partition, p.model_probability, p.model_band,
       p.baseline_probability, p.baseline_band, p.actual_breach
FROM fact_breach_risk_prediction p
JOIN v_ticket_kpi t ON t.ticket_key=p.ticket_key;
