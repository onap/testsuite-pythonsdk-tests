from time import sleep

import pytest

from onaptests.steps.base import BaseStep



class TestStep(BaseStep):

    @BaseStep.store_state
    def execute(self):
        return super().execute()

    @property
    def description(self):
        return "Test pass step"

    @property
    def component(self) -> str:
        return "Test"


class TestFailStep(BaseStep):

    @BaseStep.store_state
    def execute(self):
        super().execute()
        raise Exception

    @property
    def description(self):
        return "Test fail step"

    @property
    def component(self) -> str:
        return "Test"


class TestOneSecStep(BaseStep):

    @BaseStep.store_state
    def execute(self):
        super().execute()
        sleep(1)

    @property
    def description(self):
        return "One second test step"

    @property
    def component(self) -> str:
        return "Test"


class TestStepNoSuperExecute(BaseStep):

    @BaseStep.store_state
    def execute(self):
        sleep(1)

    @property
    def description(self):
        return "One second test step - no super execute call"

    @property
    def component(self) -> str:
        return "Test"


def test_store_state():
    ts = TestStep()
    ts.execute()
    assert len(ts.reports_collection.report) == 1
    rep = ts.reports_collection.report[0]
    assert rep.step_description == "[Test] TestStep: Test pass step"
    assert rep.step_execution_status.value == "PASS"
    assert rep.step_execution_duration != 0

    fs = TestFailStep()
    fs.add_step(TestStep())
    with pytest.raises(Exception):
        fs.execute()
    rep_f, rep_s = fs.reports_collection.report
    assert rep_f.step_description == "[Test] TestFailStep: Test fail step"
    assert rep_f.step_execution_status.value == "FAIL"
    assert rep_f.step_execution_duration != 0

    assert rep_s.step_description == "[Test] TestStep: Test pass step"
    assert rep_s.step_execution_status.value == "PASS"
    assert rep_s.step_execution_duration != 0


def test_store_state_time_measurement():

    ts = TestOneSecStep()
    ts.execute()
    assert len(ts.reports_collection.report) == 1
    rep = ts.reports_collection.report[0]
    assert rep.step_execution_duration > 1

    ts = TestOneSecStep()
    ts.add_step(TestOneSecStep())
    ts.execute()
    assert len(ts.reports_collection.report) == 2
    rep_one, rep_two = ts.reports_collection.report
    assert rep_one.step_execution_duration > 1 and rep_one.step_execution_duration < 2
    assert rep_two.step_execution_duration > 1 and rep_two.step_execution_duration < 2

    ts = TestStepNoSuperExecute()
    ts.execute()
    assert len(ts.reports_collection.report) == 1
    rep = ts.reports_collection.report[0]
    assert rep.step_execution_duration < 1
