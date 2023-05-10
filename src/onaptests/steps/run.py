import os
from onapsdk.configuration import settings
from onaptests.steps.reports_collection import ReportsCollection, Report, ReportStepStatus

settings.SERVICE_NAME = 'service'
settings.SERVICE_DETAILS = 'detailsv4'
settings.REPORTING_FILE_PATH = os.path.join(os.getcwd(), 'reports2.json') 

reports = ReportsCollection()

reports.put(Report("Step 1", ReportStepStatus.PASS, 10.0))
reports.put(Report("Step 2", ReportStepStatus.FAIL, 20.0))
reports.put(Report("Step 3", ReportStepStatus.NOT_EXECUTED, 0.0))

report_dict = reports.generate_report_json()

print(report_dict)