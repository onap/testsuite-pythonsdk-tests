#!/usr/bin/env python
"""Basic Onboard test case."""
from onaptests.scenario.scenario_base import ScenarioBase
from onaptests.steps.onboard.service import YamlTemplateServiceOnboardStep


class BasicOnboard(ScenarioBase):
    """Onboard a simple VM with ONAP."""

    def __init__(self, **kwargs):
        """Init BasicOnboard."""
        # import basic_onboard_settings needed
        super().__init__('basic_onboard', **kwargs)
        self.test = YamlTemplateServiceOnboardStep()
