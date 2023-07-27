#!/usr/bin/env python
"""Basic CPS test case."""
from onaptests.scenario.scenario_base import ScenarioBase
from onaptests.steps.onboard.cps import CreateCpsAnchorNodeStep


class BasicCps(ScenarioBase):
    """Create CPS resources:
            - dataspace
            - schemaset
            - anchor
        And create a node. Use bookstore YANG model (available on CPS repository
        https://github.com/onap/cps/blob/master/cps-service/src/test/resources/bookstore.yang).
        At the end delete what's available to be deleted.

    """

    def __init__(self, **kwargs):
        """Init Basic CPS."""
        super().__init__('basic_cps', **kwargs)
        self.test = CreateCpsAnchorNodeStep()
