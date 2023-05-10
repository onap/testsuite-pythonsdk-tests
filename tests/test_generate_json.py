import unittest
import os
from unittest import mock
from onaptests.steps.reports_collection import ReportsCollection, Report, ReportStepStatus, ReportStepStatusEncoder


class TestReportsCollection(unittest.TestCase):

    def setUp(self):
        self.collection = ReportsCollection()

    @mock.patch("onaptests.steps.reports_collection.settings")
    def test_generate_report_json(self, settings):
        settings.SERVICE_NAME = "Status Check"
        settings.SERVICE_DETAILS = "Checks status of all k8s resources in the selected namespace"
        settings.SERVICE_COMPONENTS = "ALL"
        settings.REPORTING_FILE_DIRECTORY = "/tmp/"
        settings.REPORTING_FILE_PATH = "reporting.html"
        settings.JSON_REPORTING_FILE_PATH = "reporting.json"

        self.collection.put(Report("Step 1", ReportStepStatus.PASS, 10.0))
        self.collection.put(Report("Step 2", ReportStepStatus.FAIL, 5.0))
        self.collection.put(Report("Step 3", ReportStepStatus.NOT_EXECUTED, 0.0))

        report_dict = self.collection.generate_report()

        self.assertEqual(report_dict['usecase'], 'Status Check')
        self.assertEqual(report_dict['details'], 'Checks status of all k8s resources in the selected namespace')
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
        report_json_path = os.path.join(settings.REPORTING_FILE_DIRECTORY, settings.JSON_REPORTING_FILE_PATH)
        self.assertTrue(os.path.exists(report_json_path))
        self.assertEqual(report_json_path,'/tmp/reporting.json')
        os.remove(report_json_path)

if __name__ == '__main__':
    unittest.main()
