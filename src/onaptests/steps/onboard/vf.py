from onapsdk.configuration import settings
from onapsdk.sdc.vf import Vf
from onapsdk.sdc.vsp import Vsp

from ..base import BaseStep, YamlTemplateBaseStep
from .vsp import VspOnboardStep, YamlTemplateVspOnboardStep


class VfOnboardStep(BaseStep):
    """Vf onboard step."""

    def __init__(self, cleanup=False):
        """Initialize step.

        Substeps:
            - VspOnboardStep.
        """
        super().__init__(cleanup=cleanup)
        self.add_step(VspOnboardStep(cleanup=cleanup))

    @property
    def description(self) -> str:
        """Step description."""
        return "Onboard vf in SDC."

    @BaseStep.store_state
    def execute(self):
        """Onboard Vf.

        Use settings values:
         - VSP_NAME,
         - VF_NAME.

        """
        super().execute()
        vsp: Vsp = Vsp(name=settings.VSP_NAME)
        vf: Vf = Vf(name=settings.VF_NAME, vsp=vsp)
        vf.onboard()


class YamlTemplateVfOnboardStep(YamlTemplateBaseStep):
    """Vf onboard using YAML template step."""

    def __init__(self, cleanup=False) -> None:
        """Initialize step.

        Substeps:
            - YamlTemplateVspOnboardStep.
        """
        super().__init__(cleanup=cleanup)
        self.add_step(YamlTemplateVspOnboardStep(cleanup=cleanup))

    @property
    def description(self) -> str:
        """Step description."""
        return "Onboard vf described in YAML file in SDC."

    @property
    def yaml_template(self) -> dict:
        """YAML template.

        Get YAML template from parent using it's name.

        Returns:
            dict: YAML template

        """
        return self.parent.yaml_template[self.parent.service_name]

    @YamlTemplateBaseStep.store_state
    def execute(self):
        """Onboard Vfs from YAML template."""
        super().execute()
        if "vnfs" in self.yaml_template:
            for vnf in self.yaml_template["vnfs"]:
                vsp: Vsp = Vsp(name=f"{vnf['vnf_name']}_VSP")
                vf: Vf = Vf(name=vnf['vnf_name'], vsp=vsp)
                vf.onboard()
