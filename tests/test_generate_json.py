import unittest
import os
import json
from onaptests.steps.reports_collection import ReportsCollection, Report, ReportStepStatus, ReportStepStatusEncoder
class TestReportsCollection(unittest.TestCase):
    def setUp(self):
        self.collection = ReportsCollection()
    def test_generate_report_json(self):
        self.collection.put(Report("Step 1", ReportStepStatus.PASS, 10.0))
        self.collection.put(Report("Step 2", ReportStepStatus.FAIL, 5.0))
        self.collection.put(Report("Step 3", ReportStepStatus.NOT_EXECUTED, 0.0))

        report_dict = self.collection.generate_report_json()

        path =  os.path.join(os.getcwd(), 'report.json')
        with open(path, 'w') as f:
            json.dump(report_dict, f, indent =4, cls=ReportStepStatusEncoder)

        self.assertEqual(report_dict['usecase'], 'test_healthcheck')
        self.assertEqual(report_dict['details'], '')
        self.assertEqual(report_dict['components'], 'ALL')
        self.assertEqual(len(report_dict['steps']), 3)
        step1 = report_dict['steps'][0]
        step2 = report_dict['steps'][1]
        step3 = report_dict['steps'][2]
        self.assertEqual(step1['description'], 'Step 1')
        self.assertEqual(step1['duration'], 10.0)
        self.assertEqual(step2['description'], 'Step 2')
        self.assertEqual(step2['duration'], 5.0)
        self.assertEqual(step3['description'], 'Step 3')
        self.assertEqual(step3['duration'], 0.0)
        os.remove(path)
if __name__ == '__main__':
    unittest.main()
