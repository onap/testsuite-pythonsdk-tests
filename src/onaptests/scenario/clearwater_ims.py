#!/usr/bin/env python
"""vIMS VM test case."""
from onaptests.scenario.scenario_base import ScenarioBase
from onaptests.steps.instantiate.vf_module_ala_carte import \
    YamlTemplateVfModuleAlaCarteInstantiateStep


class ClearwaterIms(ScenarioBase):
    """Onboard then instantiate a clearwater vIMS with ONAP."""

    def __init__(self, **kwargs):
        """Init Clearwater IMS."""
        # import clearwater_ims_nomulticloud_settings needed
        super().__init__('clearwater_ims', **kwargs)
        self.test = YamlTemplateVfModuleAlaCarteInstantiateStep()
