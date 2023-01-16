from onapsdk.configuration import settings
from onapsdk.sdc.vendor import Vendor
from onapsdk.sdc.vsp import Vsp
from onaptests.utils.resources import get_resource_location

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

    @property
    def description(self) -> str:
        """Step description."""
        return "Onboard vsp in SDC."

    @property
    def component(self) -> str:
        """Component name."""
        return "SDC"

    @BaseStep.store_state
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

    @BaseStep.store_state(cleanup=True)
    def cleanup(self):
        vsp: Vsp = Vsp(name=settings.VSP_NAME)
        vsp.delete()
        super().cleanup()


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
    def description(self) -> str:
        """Step description."""
        return "Onboard vsp described in YAML file in SDC."

    @property
    def component(self) -> str:
        """Component name."""
        return "SDC"

    @property
    def yaml_template(self) -> dict:
        """YAML template.

        Get YAML template from parent.

        Returns:
            dict: YAML template

        """
        if settings.MODEL_YAML_TEMPLATE:
            return self.model_yaml_template
        else:
            return self.parent.yaml_template

    @property
    def model_yaml_template(self) -> dict:
        """Model YAML template.

        Get model YAML template from parent.

        Returns:
            dict: YAML template

        """
        return self.parent.model_yaml_template

    @YamlTemplateBaseStep.store_state
    def execute(self):
        """Onboard Vsps from YAML template.

        Use settings values:
         - VENDOR_NAME.
        """
        super().execute()
        vendor: Vendor = Vendor(name=settings.VENDOR_NAME)
        if "vnfs" in self.yaml_template:
            for vnf in self.yaml_template["vnfs"]:
                with open(get_resource_location(vnf["heat_files_to_upload"]), "rb") as package:
                    vsp: Vsp = Vsp(name=f"{vnf['vnf_name']}_VSP",
                                   vendor=vendor,
                                   package=package)
                    vsp.onboard()
        elif "pnfs" in self.yaml_template:
            for pnf in self.yaml_template["pnfs"]:
                if "heat_files_to_upload" in pnf:
                    with open(get_resource_location(pnf["heat_files_to_upload"]), "rb") as package:
                        vsp: Vsp = Vsp(name=f"{pnf['pnf_name']}_VSP",
                                    vendor=vendor,
                                    package=package)
                        vsp.onboard()

    @YamlTemplateBaseStep.store_state(cleanup=True)
    def cleanup(self) -> None:
        if "vnfs" in self.yaml_template:
            for vnf in self.yaml_template["vnfs"]:
                vsp: Vsp = Vsp(name=f"{vnf['vnf_name']}_VSP")
                vsp.delete()
        elif "pnfs" in self.yaml_template:
            for pnf in self.yaml_template["pnfs"]:
                vsp: Vsp = Vsp(name=f"{pnf['pnf_name']}_VSP")
                vsp.delete()
        super().cleanup()
