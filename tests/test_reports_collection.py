
from onaptests.steps.reports_collection import ReportsCollection


def test_reports_collection():
    rc = ReportsCollection()
    assert rc.report == {}

    rc.put({"a": "b"})
    assert rc.report == {"a": "b"}
