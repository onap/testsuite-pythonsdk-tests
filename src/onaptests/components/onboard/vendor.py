from onapsdk.configuration import settings
from onapsdk.vendor import Vendor

from ..base import BaseComponent


class VendorOnboardComponent(BaseComponent):

    def __init__(self, cleanup=False):
        super().__init__(cleanup=cleanup)

    def action(self):
        super().action()
        vendor: Vendor = Vendor(name=settings.VENDOR_NAME)
        vendor.onboard()
