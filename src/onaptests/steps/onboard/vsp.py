from onapsdk.configuration import settings
from onapsdk.sdc.vendor import Vendor
from onapsdk.sdc.vsp import Vsp

from ..base import BaseStep, YamlTemplateBaseStep
from .vendor import VendorOnboardStep


class VspOnboardStep(BaseStep):
    """Vsp onboard step."""

    def __init__(self, cleanup=False):
        """Initialize step.

        Substeps:
            - VendorOnboardStep.
        """
        super().__init__(cleanup=cleanup)
        self.add_step(VendorOnboardStep(cleanup=cleanup))

    def execute(self):
        """Onboard Vsp.

        Use settings values:
         - VSP_NAME,
         - VSP_FILE_PATH,
         - VENDOR_NAME.

        """
        super().execute()
        vendor: Vendor = Vendor(name=settings.VENDOR_NAME)
        vsp: Vsp = Vsp(name=settings.VSP_NAME, vendor=vendor, package=open(settings.VSP_FILE_PATH, "rb"))
        vsp.onboard()


class YamlTemplateVspOnboardStep(YamlTemplateBaseStep):
    """Vsp onboard using YAML template step."""

    def __init__(self, cleanup=False):
        """Initialize step.

        Substeps:
            - VendorOnboardStep.
        """
        super().__init__(cleanup=cleanup)
        self.add_step(VendorOnboardStep(cleanup=cleanup))

    @property
    def yaml_template(self) -> dict:
        """YAML template.

        Get YAML template from parent.

        Returns:
            dict: YAML template

        """
        return self.parent.yaml_template

    def execute(self):
        """Onboard Vsps from YAML template.

        Use settings values:
         - VENDOR_NAME.
        """
        super().execute()
        vendor: Vendor = Vendor(name=settings.VENDOR_NAME)
        for vnf in self.yaml_template["vnfs"]:
            with open(vnf["heat_files_to_upload"], "rb") as package:
                vsp: Vsp = Vsp(name=f"{vnf['vnf_name']}_VSP", vendor=vendor, package=package)
                vsp.onboard()
