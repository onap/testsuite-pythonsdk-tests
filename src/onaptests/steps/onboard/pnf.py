"""PNF onboarding step module."""

import time
from pathlib import Path

from onapsdk.configuration import settings
from onapsdk.exceptions import ResourceNotFound
from onapsdk.sdc2.pnf import Pnf
from onapsdk.sdc2.sdc_resource import LifecycleOperation, LifecycleState
from onapsdk.sdc.vendor import Vendor
from onapsdk.sdc.vsp import Vsp

from onaptests.utils.resources import get_resource_location
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
        try:
            pnf: Pnf = Pnf.get_by_name(name=settings.PNF_NAME)
            if pnf.lifecycle_state == LifecycleState.CERTIFIED:
                return
        except ResourceNotFound:
            vsp: Vsp = Vsp(name=settings.VSP_NAME)
            pnf = Pnf.create(settings.PNF_NAME, vsp=vsp, vendor=vsp.vendor)
            pnf.add_deployment_artifact(
                artifact_type=settings.PNF_ARTIFACT_TYPE,
                artifact_name=settings.PNF_ARTIFACT_NAME,
                artifact_label=settings.PNF_ARTIFACT_LABEL,
                artifact_file_path=settings.PNF_ARTIFACT_FILE_PATH
            )
        pnf.lifecycle_operation(LifecycleOperation.CERTIFY)

    @BaseStep.store_state(cleanup=True)
    def cleanup(self):
        try:
            pnf = Pnf.get_by_name(settings.PNF_NAME)
            pnf.archive()
            pnf.delete()
        except ResourceNotFound:
            self._logger.warning("VF not created")
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
            for pnf in self.yaml_template["pnfs"]:
                if "heat_files_to_upload" in pnf:
                    vsp: Vsp = Vsp(name=f"{pnf['pnf_name']}_VSP")
                else:
                    vsp = None
                try:
                    pnf_obj: Pnf = Pnf.get_by_name(name=pnf["pnf_name"])
                    if pnf_obj.lifecycle_state == LifecycleState.CERTIFIED:
                        self._logger.info("PNF already created")
                        return
                except ResourceNotFound:
                    pnf_obj: Pnf = Pnf.create(name=pnf["pnf_name"],
                                              vsp=vsp,
                                              vendor=Vendor(name=pnf["pnf_name"]))
                    if all(x in pnf for x in ["pnf_artifact_type",
                                              "pnf_artifact_name",
                                              "pnf_artifact_label",
                                              "pnf_artifact_file_path"]):
                        artifact_file_path: Path = Path(pnf["pnf_artifact_file_path"])
                        if not artifact_file_path.exists():
                            artifact_file_path = Path(get_resource_location(artifact_file_path))
                        pnf_obj.add_deployment_artifact(
                            artifact_type=pnf["pnf_artifact_type"],
                            artifact_name=pnf["pnf_artifact_name"],
                            artifact_label=pnf["pnf_artifact_label"],
                            artifact_file_path=str(artifact_file_path)
                        )
                time.sleep(10)
                pnf_obj.lifecycle_operation(LifecycleOperation.CERTIFY)

    @YamlTemplateBaseStep.store_state(cleanup=True)
    def cleanup(self):
        if "pnfs" in self.yaml_template:
            for pnf in self.yaml_template["pnfs"]:
                try:
                    pnf_obj: Pnf = Pnf.get_by_name(name=pnf["pnf_name"])
                    pnf_obj.archive()
                    pnf_obj.delete()
                except ResourceNotFound:
                    self._logger.warning(f"PNF {pnf['pnf_name']} does not exist")
        super().cleanup()
