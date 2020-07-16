from onapsdk.configuration import settings
from onapsdk.sdc.vendor import Vendor

from ..base import BaseStep


class VendorOnboardStep(BaseStep):
    """Vendor onboard step."""

    def execute(self):
        """Onboard vendor.

        Use settings values:
         - VENDOR_NAME.

        """
        super().execute()
        vendor: Vendor = Vendor(name=settings.VENDOR_NAME)
        vendor.onboard()
