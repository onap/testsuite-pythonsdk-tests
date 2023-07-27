#!/usr/bin/env python
"""Basic CNF test case."""
from onapsdk.configuration import settings
from onaptests.scenario.scenario_base import ScenarioBase
from onaptests.steps.instantiate.vf_module_ala_carte import \
    YamlTemplateVfModuleAlaCarteInstantiateStep


class BasicCnf(ScenarioBase):
    """Onboard then instantiate a simple CNF with ONAP."""

    def __init__(self, **kwargs):
        """Init BasicCnf."""
        super().__init__('basic_cnf', **kwargs)
        self.test = YamlTemplateVfModuleAlaCarteInstantiateStep(
            cleanup=settings.CLEANUP_FLAG)
