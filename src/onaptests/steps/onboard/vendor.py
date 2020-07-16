from onapsdk.configuration import settings
from onapsdk.vendor import Vendor

from ..base import BaseStep


class VendorOnboardStep(BaseStep):

    def __init__(self, cleanup=False):
        super().__init__(cleanup=cleanup)

    def execute(self):
        super().execute()
        vendor: Vendor = Vendor(name=settings.VENDOR_NAME)
        vendor.onboard()
