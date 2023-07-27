#!/usr/bin/env python
"""Basic Onboard test case."""
from onapsdk.configuration import settings
from onaptests.scenario.scenario_base import ScenarioBase
from onaptests.steps.instantiate.sdnc_service import TestSdncStep


class BasicSdnc(ScenarioBase):
    """Create SDNC service.
    Check and delete the service.
    """

    def __init__(self, **kwargs):
        """Init Basic SDNC use case."""
        super().__init__('basic_sdnc', **kwargs)
        self.test = TestSdncStep(cleanup=settings.CLEANUP_FLAG)
