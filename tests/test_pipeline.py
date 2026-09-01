import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class PipelineTests(unittest.TestCase):
 def test_reproducible_pipeline_and_controls(self):
  subprocess.run([sys.executable,'src/generate_data.py'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
  subprocess.run([sys.executable,'src/pipeline.py'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
  report=json.loads((ROOT/'reports/data_quality_report.json').read_text()); data=json.loads((ROOT/'web/data.json').read_text())
  self.assertEqual(report['status'],'PASS'); self.assertEqual(report['reconciliation']['difference'],0); self.assertGreater(data['totals']['tickets'],500); self.assertLessEqual(data['totals']['sla_attainment'],100)
if __name__=='__main__': unittest.main()
