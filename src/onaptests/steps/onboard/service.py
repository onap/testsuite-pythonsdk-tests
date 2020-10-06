from yaml import load

from onapsdk.configuration import settings
from onapsdk.sdc.service import Service
from onapsdk.sdc.vf import Vf

from ..base import BaseStep, YamlTemplateBaseStep
from .vf import VfOnboardStep, YamlTemplateVfOnboardStep


class ServiceOnboardStep(BaseStep):
    """Service onboard step."""

    def __init__(self, cleanup=False):
        """Initialize step.

        Substeps:
            - VfOnboardStep.
        """
        super().__init__(cleanup=cleanup)
        self.add_step(VfOnboardStep(cleanup=cleanup))

    @BaseStep.store_state
    def execute(self):
        """Onboard service.

        Use settings values:
         - VF_NAME,
         - SERVICE_NAME.

        """
        super().execute()
        vf: Vf = Vf(name=settings.VF_NAME)
        service: Service = Service(name=settings.SERVICE_NAME, resources=[vf])
        service.onboard()


class YamlTemplateServiceOnboardStep(YamlTemplateBaseStep):
    """Service onboard using YAML template step."""

    def __init__(self, cleanup=False):
        """Initialize step.

        Substeps:
            - YamlTemplateVfOnboardStep.
        """
        super().__init__(cleanup=cleanup)
        self._yaml_template: dict = None
        self.add_step(YamlTemplateVfOnboardStep(cleanup=cleanup))

    @property
    def yaml_template(self) -> dict:
        """Step YAML template.

        Load from file if it's a root step, get from parent otherwise.

        Returns:
            dict: Step YAML template

        """
        if self.is_root:
            if not self._yaml_template:
                with open(settings.SERVICE_YAML_TEMPLATE, "r") as yaml_template:
                    self._yaml_template: dict = load(yaml_template)
            return self._yaml_template
        return self.parent.yaml_template

    @property
    def service_name(self) -> str:
        """Service name.

        Get from YAML template if it's a root step, get from parent otherwise.

        Returns:
            str: Service name

        """
        if self.is_root:
            return next(iter(self.yaml_template.keys()))
        else:
            return self.parent.service_name

    @YamlTemplateBaseStep.store_state
    def execute(self):
        """Onboard service."""
        super().execute()
        service: Service = Service(name=self.service_name,
                                   resources=[Vf(name=vnf["vnf_name"]) \
                                                for vnf in self.yaml_template[self.service_name]["vnfs"]])
        service.onboard()
