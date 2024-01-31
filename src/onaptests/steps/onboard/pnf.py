"""PNF onboarding step module."""

from onapsdk.configuration import settings
from onapsdk.sdc.pnf import Pnf
from onapsdk.sdc.vendor import Vendor
from onapsdk.sdc.vsp import Vsp

from ..base import BaseStep, YamlTemplateBaseStep
from .vsp import VspOnboardStep, YamlTemplateVspOnboardStep


class PnfOnboardStep(BaseStep):
    """PNF onboard step."""

    def __init__(self) -> None:
        """Step initialization.

        Substeps:
            - VendorOnboardStep.

        Args:
            cleanup(bool, optional): Determines if cleanup action should be called.

        """
        super().__init__(cleanup=settings.CLEANUP_FLAG)
        self.add_step(VspOnboardStep())

    @property
    def description(self) -> str:
        """Step description."""
        return "Onboard pnf in SDC."

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
    def execute(self) -> None:
        """Onboard PNF in SDC.

        Use settings values:
         - VENDOR_NAME,
         - PNF_NAME,
         - PNF_ARTIFACT_TYPE,
         - PNF_ARTIFACT_NAME,
         - PNF_ARTIFACT_LABEL,
         - PNF_ARTIFACT_FILE_PATH

        """
        super().execute()
        vendor: Vendor = Vendor(name=settings.VENDOR_NAME)
        pnf: Pnf = Pnf(name=settings.PNF_NAME, vendor=vendor)
        if not pnf.created():
            pnf.create()
            pnf.add_deployment_artifact(
                artifact_type=settings.PNF_ARTIFACT_TYPE,
                artifact_name=settings.PNF_ARTIFACT_NAME,
                artifact_label=settings.PNF_ARTIFACT_LABEL,
                artifact=settings.PNF_ARTIFACT_FILE_PATH
            )
            pnf.onboard()

    @BaseStep.store_state(cleanup=True)
    def cleanup(self):
        pnf: Pnf = Pnf(name=settings.PNF_NAME)
        if pnf.exists():
            pnf.archive()
            pnf.delete()
        super().cleanup()


class YamlTemplatePnfOnboardStep(YamlTemplateBaseStep):
    """PNF onboard using YAML template step."""

    def __init__(self) -> None:
        """Step initialization.

        Substeps:
            - VendorOnboardStep.

        Args:
            cleanup(bool, optional): Determines if cleanup action should be called.

        """
        super().__init__(cleanup=settings.CLEANUP_FLAG)
        self.add_step(YamlTemplateVspOnboardStep())

    @property
    def description(self) -> str:
        """Step description."""
        return "Onboard pnf using YAML template in SDC."

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

        Get YAML template from parent using it's name.

        Returns:
            dict: YAML template

        """
        return self.parent.yaml_template[self.parent.service_name]

    @property
    def model_yaml_template(self) -> dict:
        return {}

    @YamlTemplateBaseStep.store_state
    def execute(self):
        """Onboard PNFs from YAML template."""
        super().execute()
        if "pnfs" in self.yaml_template:
            vendor: Vendor = Vendor(name=settings.VENDOR_NAME)
            for pnf in self.yaml_template["pnfs"]:
                if "heat_files_to_upload" in pnf:
                    vsp: Vsp = Vsp(name=f"{pnf['pnf_name']}_VSP")
                else:
                    vsp = None
                pnf_obj: Pnf = Pnf(name=pnf["pnf_name"], vendor=vendor, vsp=vsp)
                if not pnf_obj.created():
                    pnf_obj.create()
                    pnf_obj.add_deployment_artifact(
                        artifact_type=pnf["pnf_artifact_type"],
                        artifact_name=pnf["pnf_artifact_name"],
                        artifact_label=pnf["pnf_artifact_label"],
                        artifact=pnf["pnf_artifact_file_path"]
                    )
                    pnf_obj.onboard()

    @YamlTemplateBaseStep.store_state(cleanup=True)
    def cleanup(self):
        if "pnfs" in self.yaml_template:
            for pnf in self.yaml_template["pnfs"]:
                pnf_obj: Pnf = Pnf(name=pnf["pnf_name"])
                if pnf_obj.exists():
                    pnf_obj.archive()
                    pnf_obj.delete()
        super().cleanup()
