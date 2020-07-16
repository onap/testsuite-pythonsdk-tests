from onapsdk.configuration import settings
from onapsdk.vendor import Vendor
from onapsdk.vsp import Vsp

from ..base import BaseStep, YamlTemplateBaseStep
from .vendor import VendorOnboardStep


class VspOnboardStep(BaseStep):

    def __init__(self, cleanup=False):
        super().__init__(cleanup=cleanup)
        self.add_step(VendorOnboardStep(cleanup=cleanup))

    def execute(self):
        super().execute()
        vendor: Vendor = Vendor(name=settings.VENDOR_NAME)
        vsp: Vsp = Vsp(name=settings.VSP_NAME, vendor=vendor, package=open(settings.VSP_FILE_PATH, "rb"))
        vsp.onboard()


class YamlTemplateVspOnboardStep(VspOnboardStep, YamlTemplateBaseStep):

    @property
    def yaml_template(self) -> dict:
        return self.parent.yaml_template

    def execute(self):
        super().execute()
        vendor: Vendor = Vendor(name=settings.VENDOR_NAME)
        for vnf in self.yaml_template["vnfs"]:
            with open(vnf["heat_files_to_upload"], "rb") as package:
                vsp: Vsp = Vsp(name=f"{vnf['vnf_name']}_VSP", vendor=vendor, package=package)
                vsp.onboard()
