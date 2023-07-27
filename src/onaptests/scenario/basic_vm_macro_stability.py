"""Instantiate basic vm using SO macro flow."""
from onapsdk.configuration import settings
from onapsdk.exceptions import SDKException
from onaptests.scenario.scenario_base import ScenarioBase
from onaptests.steps.instantiate.service_macro import \
    YamlTemplateServiceMacroInstantiateStep
from onaptests.utils.exceptions import OnapTestException


class BasicVmMacroStability(ScenarioBase):
    """Instantiate a basic vm macro."""

    def __init__(self, **kwargs):
        """Init Basic Macro use case."""
        super().__init__('basic_vm_macro_stability', **kwargs)
        self.test = YamlTemplateServiceMacroInstantiateStep(cleanup=settings.CLEANUP_FLAG)
