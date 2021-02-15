from time import sleep

import pytest

from onaptests.steps.base import BaseStep
from onaptests.utils.exceptions import OnapTestException



class TestStep(BaseStep):

    @BaseStep.store_state
    def execute(self):
        return super().execute()

    @BaseStep.store_state(cleanup=True)
    def cleanup(self) -> None:
        return super().cleanup()

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
        raise OnapTestException

    @BaseStep.store_state(cleanup=True)
    def cleanup(self) -> None:
        raise OnapTestException

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


class TestCleanupStepA(BaseStep):

    @BaseStep.store_state
    def execute(self):
        return super().execute()

    @BaseStep.store_state(cleanup=True)
    def cleanup(self):
        return super().cleanup()

    @property
    def description(self):
        return "Test cleanup step A"

    @property
    def component(self) -> str:
        return "Test"


class TestCleanupStepB(TestCleanupStepA):

    @property
    def description(self):
        return "Test cleanup step B"


class TestCleanupStepC(TestCleanupStepA):

    @property
    def description(self):
        return "Test cleanup step C"


class TestCleanupStepD(TestCleanupStepA):

    @property
    def description(self):
        return "Test cleanup step D"


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

    ts = TestStep(cleanup=True)
    ts.add_step(TestFailStep(cleanup=True))
    with pytest.raises(Exception):
        ts.execute()
    with pytest.raises(Exception):
        ts.cleanup()
    assert len(ts.reports_collection.report) == 4
    cln_rep_f, cln_rep_s, rep_s, rep_f = ts.reports_collection.report
    assert rep_f.step_description == "[Test] TestFailStep: Test fail step"
    assert rep_f.step_execution_status.value == "FAIL"
    assert rep_f.step_execution_duration != 0

    assert rep_s.step_description == "[Test] TestStep: Test pass step"
    assert rep_s.step_execution_status.value == "NOT EXECUTED"
    assert rep_s.step_execution_duration != 0

    assert cln_rep_s.step_description == "[Test] TestStep cleanup: Test pass step"
    assert cln_rep_s.step_execution_status.value == "PASS"
    assert cln_rep_s.step_execution_duration != 0

    assert cln_rep_f.step_description == "[Test] TestFailStep cleanup: Test fail step"
    assert cln_rep_f.step_execution_status.value == "FAIL"
    assert cln_rep_f.step_execution_duration != 0

    ts = TestStep(cleanup=True)
    tsf = TestFailStep(cleanup=True)
    tsf.add_step(TestStep(cleanup=True))
    ts.add_step(tsf)
    ts.add_step(TestStep(cleanup=True))
    with pytest.raises(Exception):
        ts.execute()
    with pytest.raises(Exception):
        ts.cleanup()

    assert len(ts.reports_collection.report) == 5
    cln_2, cln_1, exec_3, exec_2, exec_1 = ts.reports_collection.report

    assert exec_1.step_description == "[Test] TestStep: Test pass step"
    assert exec_1.step_execution_status.value == "PASS"
    assert exec_1.step_execution_duration != 0

    assert exec_2.step_description == "[Test] TestFailStep: Test fail step"
    assert exec_2.step_execution_status.value == "FAIL"
    assert exec_2.step_execution_duration != 0

    assert exec_3.step_description == "[Test] TestStep: Test pass step"
    assert exec_3.step_execution_status.value == "NOT EXECUTED"
    assert exec_3.step_execution_duration != 0

    assert cln_1.step_description == "[Test] TestStep cleanup: Test pass step"
    assert cln_1.step_execution_status.value == "PASS"
    assert cln_1.step_execution_duration != 0

    assert cln_2.step_description == "[Test] TestFailStep cleanup: Test fail step"
    assert cln_2.step_execution_status.value == "FAIL"
    assert cln_2.step_execution_duration != 0


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


def test_store_state_with_cleanup():

    ts = TestCleanupStepA(cleanup=True)
    ts_b = TestCleanupStepB(cleanup=True)
    ts_b.add_step(TestCleanupStepC(cleanup=True))
    ts.add_step(ts_b)
    ts.add_step(TestCleanupStepD(cleanup=True))
    ts.execute()
    ts.cleanup()
    assert len(ts.reports_collection.report) == 8
    (rep_cleanup_step_4, rep_cleanup_step_3, rep_cleanup_step_2, rep_cleanup_step_1,
        rep_exec_step_4, rep_exec_step_3, rep_exec_step_2, rep_exec_step_1) = ts.reports_collection.report
    assert rep_exec_step_1.step_description == "[Test] TestCleanupStepC: Test cleanup step C"
    assert rep_exec_step_2.step_description == "[Test] TestCleanupStepB: Test cleanup step B"
    assert rep_exec_step_3.step_description == "[Test] TestCleanupStepD: Test cleanup step D"
    assert rep_exec_step_4.step_description == "[Test] TestCleanupStepA: Test cleanup step A"
    assert rep_cleanup_step_1.step_description == "[Test] TestCleanupStepA cleanup: Test cleanup step A"
    assert rep_cleanup_step_2.step_description == "[Test] TestCleanupStepB cleanup: Test cleanup step B"
    assert rep_cleanup_step_3.step_description == "[Test] TestCleanupStepC cleanup: Test cleanup step C"
    assert rep_cleanup_step_4.step_description == "[Test] TestCleanupStepD cleanup: Test cleanup step D"
