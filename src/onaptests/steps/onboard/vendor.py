from onapsdk.configuration import settings
from onapsdk.sdc.vendor import Vendor

from ..base import BaseStep, YamlTemplateBaseStep


class VendorOnboardStep(BaseStep):
    """Vendor onboard step."""

    def __init__(self):
        """Initialize step."""
        super().__init__(cleanup=settings.CLEANUP_FLAG)

    @property
    def description(self) -> str:
        """Step description."""
        return "Onboard vendor in SDC."

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
        """Onboard vendor.

        Use settings values:
         - VENDOR_NAME.

        """
        super().execute()
        vendor: Vendor = Vendor(name=settings.VENDOR_NAME)
        vendor.onboard()

    @BaseStep.store_state(cleanup=True)
    def cleanup(self) -> None:
        vendor: Vendor = Vendor(name=settings.VENDOR_NAME)
        if vendor.exists():
            try:
                vendor.archive()
            except Exception:
                self._logger.warning(f"Vendor {settings.VENDOR_NAME} archive failed")
            vendor.delete()
        super().cleanup()


class YamlTemplateVendorOnboardStep(YamlTemplateBaseStep):
    """Vendor onboard using YAML template step."""

    def __init__(self):
        """Initialize step. """
        super().__init__(cleanup=settings.CLEANUP_FLAG)

    @property
    def description(self) -> str:
        """Step description."""
        return "Onboard vendor described in YAML file in SDC."

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
                vendor: Vendor = Vendor(name=f"{vnf['vnf_name']}")
                vendor.onboard()
        elif "pnfs" in self.yaml_template:
            for pnf in self.yaml_template["pnfs"]:
                vendor: Vendor = Vendor(name=f"{pnf['pnf_name']}")
                vendor.onboard()

    def _cleanup_vendor(self, name):
        vendor: Vendor = Vendor(name=name)
        if vendor.exists():
            try:
                vendor.archive()
            except Exception:
                self._logger.warning(f"Vendor {name} archive failed")
            vendor.delete()

    @YamlTemplateBaseStep.store_state(cleanup=True)
    def cleanup(self) -> None:
        if "vnfs" in self.yaml_template:
            for vnf in self.yaml_template["vnfs"]:
                self._cleanup_vendor(f"{vnf['vnf_name']}")
        elif "pnfs" in self.yaml_template:
            for pnf in self.yaml_template["pnfs"]:
                self._cleanup_vendor(f"{pnf['pnf_name']}")
        super().cleanup()
