import pytest

from onaptests.steps.base import BaseStep



class TestStep(BaseStep):

    @BaseStep.store_state
    def execute(self):
        return super().execute()

    @property
    def description(self):
        return "Test pass step"


class TestFailStep(BaseStep):

    @BaseStep.store_state
    def execute(self):
        super().execute()
        raise Exception

    @property
    def description(self):
        return "Test fail step"


def test_store_state():
    ts = TestStep()
    ts.execute()
    assert len(ts.reports_collection.report) == 1
    rep = ts.reports_collection.report[0]
    assert rep.step_description == "TestStep: Test pass step"
    assert rep.step_execution_status.value == "PASS"
    assert rep.step_execution_duration != 0

    fs = TestFailStep()
    fs.add_step(TestStep())
    with pytest.raises(Exception):
        fs.execute()
    rep_f, rep_s = fs.reports_collection.report
    assert rep_f.step_description == "TestFailStep: Test fail step"
    assert rep_f.step_execution_status.value == "FAIL"
    assert rep_f.step_execution_duration != 0

    assert rep_s.step_description == "TestStep: Test pass step"
    assert rep_s.step_execution_status.value == "PASS"
    assert rep_s.step_execution_duration != 0
