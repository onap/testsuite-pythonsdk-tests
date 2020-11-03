
from onaptests.steps.reports_collection import Report, ReportsCollection, ReportStepStatus


def test_reports_collection():
    rc = ReportsCollection()
    assert rc.report == []

    rc.put(Report(
        "test",
        ReportStepStatus.PASS,
        0.0
    ))
    assert len(rc.report) == 1


def test_reports_collection_failed_steps_num():

    rc = ReportsCollection()
    assert rc.failed_steps_num == 0

    rc.put(Report(
        "test",
        ReportStepStatus.PASS,
        0.0
    ))
    assert rc.failed_steps_num == 0

    rc.put(Report(
        "test",
        ReportStepStatus.FAIL,
        0.0
    ))
    assert rc.failed_steps_num == 1
