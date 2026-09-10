import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
import pipeline

class EdgeCaseTests(unittest.TestCase):
    def base(self):
        return {'ticket_id':'INC-99999','created_at':'2025-08-31T01:00','first_response_at':'2025-08-31T02:00+00:00','resolved_at':'','priority':'P3','category':'Access','initial_queue':'Network','response_target_hours':'16','resolution_target_hours':'48','reopened':'False','state':'OPEN'}
    def test_timezone_is_normalized_and_open_resolution_is_nullable(self):
        row=pipeline.clean_tickets([self.base()])[0]
        self.assertEqual(row['created_at'],'2025-08-31T01:00+00:00'); self.assertEqual(row['resolved_at'],''); self.assertFalse(row['reopened'])
    def test_orphan_and_reversed_assignment_events_fail(self):
        ticket=pipeline.clean_tickets([self.base()]); event={'ticket_id':'INC-99999','sequence':'1','queue':'Network','assigned_at':'2025-08-31T03:00','unassigned_at':'2025-08-31T02:00'}
        with self.assertRaises(pipeline.DataQualityError): pipeline.clean_events([event],{ticket[0]['ticket_id']})
        event['unassigned_at']='2025-08-31T04:00'; event['ticket_id']='INC-00000'
        with self.assertRaises(pipeline.DataQualityError): pipeline.clean_events([event],{ticket[0]['ticket_id']})
