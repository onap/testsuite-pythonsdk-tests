#!/usr/bin/env python
"""Basic VM test case."""
from onaptests.scenario.scenario_base import ScenarioBase
from onaptests.steps.instantiate.vf_module_ala_carte import \
    YamlTemplateVfModuleAlaCarteInstantiateStep


class BasicVm(ScenarioBase):
    """Onboard then instantiate a simple VM with ONAP."""

    def __init__(self, **kwargs):
        """Init BasicVM."""
        super().__init__('basic_vm', **kwargs)
        self.test = YamlTemplateVfModuleAlaCarteInstantiateStep()
