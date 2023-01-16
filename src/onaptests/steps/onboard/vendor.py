from onapsdk.configuration import settings
from onapsdk.sdc.vendor import Vendor

from ..base import BaseStep


class VendorOnboardStep(BaseStep):
    """Vendor onboard step."""

    @property
    def description(self) -> str:
        """Step description."""
        return "Onboard vendor in SDC."

    @property
    def component(self) -> str:
        """Component name."""
        return "SDC"

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
        if settings.SDC_CLEANUP:
            vendor: Vendor = Vendor(name=settings.VENDOR_NAME)
            vendor.archive()
            vendor.delete()
        super().cleanup()
