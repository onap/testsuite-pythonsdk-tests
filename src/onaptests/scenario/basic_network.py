#!/usr/bin/env python
"""Basic VM test case."""
from onapsdk.configuration import settings
from onaptests.scenario.scenario_base import ScenarioBase
from onaptests.steps.instantiate.vl_ala_carte import \
    YamlTemplateVlAlaCarteInstantiateStep


class BasicNetwork(ScenarioBase):
    """Onboard then instantiate a simple Network with ONAP."""

    def __init__(self, **kwargs):
        """Init Basic Network use case."""
        # import basic_network_nomulticloud_settings needed
        super().__init__('basic_network', **kwargs)
        self.test = YamlTemplateVlAlaCarteInstantiateStep(
            cleanup=settings.CLEANUP_FLAG)
