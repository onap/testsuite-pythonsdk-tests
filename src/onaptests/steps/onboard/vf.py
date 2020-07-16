from onapsdk.configuration import settings
from onapsdk.vf import Vf
from onapsdk.vsp import Vsp

from ..base import BaseStep, YamlTemplateBaseStep
from .vsp import VspOnboardStep, YamlTemplateVspOnboardStep


class VfOnboardStep(BaseStep):

    def __init__(self, cleanup=False):
        super().__init__(cleanup=cleanup)
        self.add_step(VspOnboardStep(cleanup=cleanup))

    def execute(self):
        super().execute()
        vsp: Vsp = Vsp(name=settings.VSP_NAME)
        vf: Vf = Vf(name=settings.VF_NAME, vsp=vsp)
        vf.onboard()


class YamlTemplateVfOnboardStep(YamlTemplateBaseStep):

    def __init__(self, cleanup=False) -> None:
        super().__init__(cleanup=cleanup)
        self.add_step(YamlTemplateVspOnboardStep(cleanup=cleanup))

    @property
    def yaml_template(self) -> dict:
        return self.parent.yaml_template[self.parent.name]

    def execute(self):
        super().execute()
        for vnf in self.yaml_template["vnfs"]:
            vsp: Vsp = Vsp(name=f"{vnf['vnf_name']}_VSP")
            vf: Vf = Vf(name=vnf['vnf_name'], vsp=vsp)
            vf.onboard()
