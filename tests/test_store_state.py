import pytest
from onaptests.steps.base import BaseStep


class TestStep(BaseStep):

    @BaseStep.store_state
    def execute(self):
        return super().execute()


class TestFailStep(BaseStep):

    @BaseStep.store_state
    def execute(self):
        super().execute()
        raise Exception


def test_store_state():
    ts = TestStep()
    ts.execute()
    assert ts.reports_collection.report == {"TestStep": "PASS"}

    fs = TestFailStep()
    fs.add_step(TestStep())
    with pytest.raises(Exception):
        fs.execute()
    fs.reports_collection.report == {"TestFailStep": "FAIL", "TestStep": "PASS"}
