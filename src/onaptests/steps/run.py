from onaptests.steps.reports_collection import ReportsCollection, Report, ReportStepStatus

reports = ReportsCollection()

reports.put(Report("Step 1", ReportStepStatus.PASS, 10.0))
reports.put(Report("Step 2", ReportStepStatus.FAIL, 20.0))
reports.put(Report("Step 3", ReportStepStatus.NOT_EXECUTED, 0.0))

report_dict = reports.generate_report_json()

print(report_dict)