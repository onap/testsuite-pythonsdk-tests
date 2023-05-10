import unittest
import os
import json
from unittest import mock
from onaptests.steps.reports_collection import ReportsCollection, Report, ReportStepStatus


class TestReportsCollection(unittest.TestCase):

    def setUp(self):
        self.collection = ReportsCollection()

    @mock.patch("onaptests.steps.reports_collection.settings")
    def test_generate_report_json(self, settings):
        settings.SERVICE_NAME = "Status Check"
        settings.SERVICE_DETAILS = "Checks status of all k8s resources in the selected namespace"
        settings.SERVICE_COMPONENTS = "ALL"
        settings.REPORTING_FILE_DIRECTORY = "/tmp/"
        settings.HTML_REPORTING_FILE_NAME = "reporting.html"
        settings.JSON_REPORTING_FILE_NAME = "reporting.json"

        self.collection.put(Report("Step 1", ReportStepStatus.PASS, 10.0))
        self.collection.put(Report("Step 2", ReportStepStatus.FAIL, 5.0))
        self.collection.put(Report("Step 3", ReportStepStatus.NOT_EXECUTED, 0.0))
        self.collection.put(Report("Step 10", ReportStepStatus.NOT_EXECUTED, 0.0))
        self.collection.put(Report("Step 12", ReportStepStatus.PASS, 20.0))
        self.collection.put(Report("Step 21", ReportStepStatus.FAIL, 15.0))

        report_dict = self.collection.generate_report()
        report_json_path = os.path.join(settings.REPORTING_FILE_DIRECTORY, settings.JSON_REPORTING_FILE_NAME)
        self.assertTrue(os.path.exists(report_json_path))
  
        with open(report_json_path, 'r') as file:
            report_dict = json.load(file)

        self.assertEqual(report_dict['usecase'], 'Status Check')
        self.assertEqual(report_dict['details'], 'Checks status of all k8s resources in the selected namespace')
        self.assertEqual(report_dict['components'], 'ALL')
        self.assertEqual(len(report_dict['steps']), 6)
        step1 = report_dict['steps'][0]
        step2 = report_dict['steps'][1]
        step3 = report_dict['steps'][2]
        step10 = report_dict['steps'][3]
        step12 = report_dict['steps'][4]
        step21 = report_dict['steps'][5]
        self.assertEqual(step1['description'], 'Step 1')
        self.assertEqual(step1['duration'], 10.0)
        self.assertEqual(step2['description'], 'Step 2')
        self.assertEqual(step2['duration'], 5.0)
        self.assertEqual(step3['description'], 'Step 3')
        self.assertEqual(step3['duration'], 0.0)
        self.assertEqual(step10['description'], 'Step 10')
        self.assertEqual(step10['duration'], 0.0)
        self.assertEqual(step12['description'], 'Step 12')
        self.assertEqual(step12['duration'], 20.0)
        self.assertEqual(step21['description'], 'Step 21')
        self.assertEqual(step21['duration'], 15.0)
        report_json_path = os.path.join(settings.REPORTING_FILE_DIRECTORY, settings.JSON_REPORTING_FILE_NAME)
        self.assertTrue(os.path.exists(report_json_path))
        self.assertEqual(report_json_path,'/tmp/reporting.json')
        os.remove(report_json_path)

if __name__ == '__main__':
    unittest.main()
