"""PNF onboarding step module."""

from onapsdk.configuration import settings
from onapsdk.sdc.pnf import Pnf
from onapsdk.sdc.vendor import Vendor
from ..base import BaseStep
from .vendor import VendorOnboardStep


class PnfOnboardStep(BaseStep):
    """PNF onboard step."""

    def __init__(self, cleanup: bool = False) -> None:
        """Step initialization.

        Substeps:
            - VendorOnboardStep.

        Args:
            cleanup(bool, optional): Determines if cleanup action should be called.

        """
        super().__init__(cleanup=cleanup)
        self.add_step(VendorOnboardStep(cleanup=cleanup))

    @property
    def description(self) -> str:
        """Step description."""
        return "Onboard pnf in SDC."

    @property
    def component(self) -> str:
        """Component name."""
        return "SDC"

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
        vendor: Vendor = Vendor(name=settings.VENDOR_NAME)
        pnf: Pnf = Pnf(name=settings.PNF_NAME, vendor=vendor)
        pnf.create()
        pnf.add_deployment_artifact(
            artifact_type=settings.PNF_ARTIFACT_TYPE,
            artifact_name=settings.PNF_ARTIFACT_NAME,
            artifact_label=settings.PNF_ARTIFACT_LABEL,
            artifact=settings.PNF_ARTIFACT_FILE_PATH
        )
        pnf.onboard()
