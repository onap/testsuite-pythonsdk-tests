from yaml import load

from onapsdk.configuration import settings
from onapsdk.service import Service
from onapsdk.vf import Vf

from ..base import BaseStep, YamlTemplateBaseStep
from .vf import VfOnboardStep, YamlTemplateVfOnboardStep


class ServiceOnboardStep(BaseStep):

    def __init__(self, cleanup=False):
        super().__init__(cleanup=cleanup)
        self.add_step(VfOnboardStep(cleanup=cleanup))

    def execute(self):
        super().execute()
        vf: Vf = Vf(name=settings.VF_NAME)
        service: Service = Service(name=settings.SERVICE_NAME, resources=[vf])
        service.onboard()


class YamlTemplateServiceOnboardStep(YamlTemplateBaseStep):

    def __init__(self, cleanup=False):
        super().__init__(cleanup=cleanup)
        self._yaml_template: dict = None
        self.add_step(YamlTemplateVfOnboardStep(cleanup=cleanup))

    @property
    def yaml_template(self) -> dict:
        if self.is_root:
            if not self._yaml_template:
                with open(settings.SERVICE_YAML_TEMPLATE, "r") as yaml_template:
                    self._yaml_template: dict = load(yaml_template)
            return self._yaml_template
        return self.parent.yaml_template

    @property
    def name(self) -> str:
        if self.is_root:
            return next(iter(self.yaml_template.keys()))
        else:
            return self.parent.service_name

    def execute(self):
        super().execute()
        service: Service = Service(name=self.name,
                                   resources=[Vf(name=vnf["vnf_name"]) \
                                                for vnf in self.yaml_template[self.name]["vnfs"]])
        service.onboard()
