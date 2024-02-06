import onapsdk.constants as const
from onapsdk.configuration import settings
from onapsdk.sdc.vendor import Vendor
from onapsdk.sdc.vsp import Vsp

from onaptests.utils.resources import get_resource_location

from ..base import BaseStep, YamlTemplateBaseStep
from .vendor import VendorOnboardStep, YamlTemplateVendorOnboardStep


class VspOnboardStep(BaseStep):
    """Vsp onboard step."""

    def __init__(self):
        """Initialize step.

        Substeps:
            - VendorOnboardStep.
        """
        super().__init__(cleanup=settings.CLEANUP_FLAG)
        self.add_step(VendorOnboardStep())

    @property
    def description(self) -> str:
        """Step description."""
        return "Onboard vsp in SDC."

    @property
    def component(self) -> str:
        """Component name."""
        return "SDC"

    def check_preconditions(self, cleanup=False) -> bool:
        if not super().check_preconditions(cleanup):
            return False
        if cleanup:
            return settings.SDC_CLEANUP
        return True

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
        with open(settings.VSP_FILE_PATH, "rb") as vsp_file:
            vsp: Vsp = Vsp(name=settings.VSP_NAME,
                           vendor=vendor,
                           package=vsp_file)
            vsp.onboard()

    @BaseStep.store_state(cleanup=True)
    def cleanup(self):
        vsp: Vsp = Vsp(name=settings.VSP_NAME)
        if vsp.exists():
            if vsp.status == const.CERTIFIED:
                vsp.archive()
            vsp.delete()
        super().cleanup()


class YamlTemplateVspOnboardStep(YamlTemplateBaseStep):
    """Vsp onboard using YAML template step."""

    def __init__(self):
        """Initialize step.

        Substeps:
            - VendorOnboardStep.
        """
        super().__init__(cleanup=settings.CLEANUP_FLAG)
        self.add_step(YamlTemplateVendorOnboardStep())

    @property
    def description(self) -> str:
        """Step description."""
        return "Onboard vsp described in YAML file in SDC."

    @property
    def component(self) -> str:
        """Component name."""
        return "SDC"

    def check_preconditions(self, cleanup=False) -> bool:
        if not super().check_preconditions(cleanup):
            return False
        if cleanup:
            return settings.SDC_CLEANUP
        return True

    @property
    def yaml_template(self) -> dict:
        """YAML template.

        Get YAML template from parent.

        Returns:
            dict: YAML template

        """
        if settings.MODEL_YAML_TEMPLATE:
            return self.model_yaml_template
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
        if "vnfs" in self.yaml_template:
            for vnf in self.yaml_template["vnfs"]:
                with open(get_resource_location(vnf["heat_files_to_upload"]), "rb") as package:
                    vsp: Vsp = Vsp(name=f"{vnf['vnf_name']}_VSP",
                                   vendor=Vendor(name=f"{vnf['vnf_name']}"),
                                   package=package)
                    vsp.onboard()
        elif "pnfs" in self.yaml_template:
            for pnf in self.yaml_template["pnfs"]:
                if "heat_files_to_upload" in pnf:
                    with open(get_resource_location(pnf["heat_files_to_upload"]), "rb") as package:
                        vsp: Vsp = Vsp(name=f"{pnf['pnf_name']}_VSP",
                                       vendor=Vendor(name=f"{pnf['pnf_name']}"),
                                       package=package)
                        vsp.onboard()

    def _cleanup_vsp(self, name):
        vsp: Vsp = Vsp(name=name)
        if vsp.exists():
            if vsp.status == const.CERTIFIED:
                vsp.archive()
            vsp.delete()

    @YamlTemplateBaseStep.store_state(cleanup=True)
    def cleanup(self) -> None:
        if "vnfs" in self.yaml_template:
            for vnf in self.yaml_template["vnfs"]:
                self._cleanup_vsp(f"{vnf['vnf_name']}_VSP")
        elif "pnfs" in self.yaml_template:
            for pnf in self.yaml_template["pnfs"]:
                self._cleanup_vsp(f"{pnf['pnf_name']}_VSP")
        super().cleanup()
