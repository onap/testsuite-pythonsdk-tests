import time
from pathlib import Path

from onapsdk.configuration import settings
from onapsdk.sdc.vf import Vf
from onapsdk.sdc.vsp import Vsp

from onaptests.utils.resources import get_resource_location

from ..base import BaseStep, YamlTemplateBaseStep
from .vsp import VspOnboardStep, YamlTemplateVspOnboardStep


class VfOnboardStep(BaseStep):
    """Vf onboard step."""

    def __init__(self):
        """Initialize step.

        Substeps:
            - VspOnboardStep.
        """
        super().__init__(cleanup=settings.CLEANUP_FLAG)
        self.add_step(VspOnboardStep())

    @property
    def description(self) -> str:
        """Step description."""
        return "Onboard vf in SDC."

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
        """Onboard Vf.

        Use settings values:
         - VSP_NAME,
         - VF_NAME.

        """
        super().execute()
        vsp: Vsp = Vsp(name=settings.VSP_NAME)
        vf: Vf = Vf(name=settings.VF_NAME, vsp=vsp)
        if not vf.created():
            vf.onboard()

    @BaseStep.store_state(cleanup=True)
    def cleanup(self):
        vf: Vf = Vf(name=settings.VF_NAME)
        if vf.exists():
            vf.archive()
            vf.delete()
        super().cleanup()


class YamlTemplateVfOnboardStep(YamlTemplateBaseStep):
    """Vf onboard using YAML template step."""

    def __init__(self) -> None:
        """Initialize step.

        Substeps:
            - YamlTemplateVspOnboardStep.
        """
        super().__init__(cleanup=settings.CLEANUP_FLAG)
        self.add_step(YamlTemplateVspOnboardStep())

    @property
    def description(self) -> str:
        """Step description."""
        return "Onboard vf described in YAML file in SDC."

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
        if settings.MODEL_YAML_TEMPLATE:
            return self.model_yaml_template
        return self.parent.yaml_template[self.parent.service_name]

    @property
    def model_yaml_template(self) -> dict:
        """Step Model YAML template.

        Load from file if it's a root step, get from parent otherwise.

        Returns:
            dict: Step YAML template

        """
        return self.parent.model_yaml_template[self.parent.service_name]

    @YamlTemplateBaseStep.store_state
    def execute(self):
        """Onboard Vfs from YAML template."""
        super().execute()
        if "vnfs" in self.yaml_template:
            for vnf in self.yaml_template["vnfs"]:
                vsp: Vsp = Vsp(name=f"{vnf['vnf_name']}_VSP")
                vf: Vf = Vf(name=vnf['vnf_name'], vsp=vsp)
                if not vf.created():
                    if all(x in vnf for x in ["vnf_artifact_type",
                                              "vnf_artifact_name",
                                              "vnf_artifact_label",
                                              "vnf_artifact_file_path"]):
                        vf.create()
                        artifact_file_path: Path = Path(vnf["vnf_artifact_file_path"])
                        if not artifact_file_path.exists():
                            artifact_file_path = Path(get_resource_location(artifact_file_path))
                        vf.add_deployment_artifact(
                            artifact_type=vnf["vnf_artifact_type"],
                            artifact_name=vnf["vnf_artifact_name"],
                            artifact_label=vnf["vnf_artifact_label"],
                            artifact=str(artifact_file_path)
                        )
                    time.sleep(10)
                    vf.onboard()

    @YamlTemplateBaseStep.store_state(cleanup=True)
    def cleanup(self):
        if "vnfs" in self.yaml_template:
            for vnf in self.yaml_template["vnfs"]:
                vf_obj: Vf = Vf(name=vnf["vnf_name"])
                if vf_obj.exists():
                    vf_obj.archive()
                    vf_obj.delete()
        super().cleanup()
