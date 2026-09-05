import json
import sqlite3
import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import pipeline

class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable,'src/generate_data.py'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
        subprocess.run([sys.executable,'src/pipeline.py'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
        subprocess.run([sys.executable,'src/advanced_analytics.py'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)

    def test_generated_quality_report_reconciles_all_layers(self):
        report=json.loads((ROOT/'reports/data_quality_report.json').read_text())
        self.assertEqual(report['status'],'PASS')
        self.assertEqual(report['reconciliation']['raw_to_staging_tickets'],0)
        self.assertEqual(report['reconciliation']['staging_to_fact_tickets'],0)
        self.assertEqual(report['reconciliation']['raw_to_staging_events'],0)
        self.assertEqual(report['reconciliation']['staging_to_fact_events'],0)
        self.assertTrue(report['reconciliation']['transfer_value_reconciled'])
        self.assertEqual(report['checks']['referential_integrity'],'PASS')
        self.assertLessEqual(report['checks']['freshness']['age_hours'],168)

    def test_star_schema_is_loaded_at_explicit_grain(self):
        con=sqlite3.connect(ROOT/'data/sla_forge.db')
        self.assertEqual(con.execute('select count(*) from fact_ticket_sla').fetchone()[0],720)
        self.assertGreater(con.execute('select count(*) from fact_assignment').fetchone()[0],720)
        self.assertEqual(con.execute('select count(*) from dim_priority').fetchone()[0],4)
        self.assertEqual(con.execute('pragma foreign_key_check').fetchall(),[])
        self.assertEqual(con.execute('select count(*) from v_ticket_kpi').fetchone()[0],720)
        self.assertEqual(con.execute('select count(*) from v_queue_kpi').fetchone()[0],5)
        self.assertGreater(con.execute('select count(*) from v_ticket_exception').fetchone()[0],0)
        con.close()

    def test_advanced_model_is_governed_and_beats_rule_baseline_auc(self):
        report=json.loads((ROOT/'reports/model_evaluation.json').read_text())
        con=sqlite3.connect(ROOT/'data/sla_forge.db')
        self.assertEqual(con.execute('select count(*) from model_run').fetchone()[0],1)
        self.assertEqual(con.execute('select count(*) from fact_breach_risk_prediction').fetchone()[0],720)
        self.assertEqual(con.execute('select count(*) from v_breach_risk_decision_support').fetchone()[0],720)
        self.assertGreater(report['model_test_metrics']['auc'],report['rule_baseline_test_metrics']['auc'])
        con.close()

    def test_duplicate_and_invalid_controlled_values_fail(self):
        rows=[{'ticket_id':'INC-00001','created_at':'2025-08-31T01:00','first_response_at':'2025-08-31T02:00','resolved_at':'','priority':'P3','category':'Access','initial_queue':'Network','response_target_hours':'16','resolution_target_hours':'48','reopened':'False','state':'Open'}]
        with self.assertRaises(pipeline.DataQualityError): pipeline.clean_tickets(rows*2)
        rows[0]['priority']='P9'
        with self.assertRaises(pipeline.DataQualityError): pipeline.clean_tickets(rows)

if __name__=='__main__': unittest.main()
