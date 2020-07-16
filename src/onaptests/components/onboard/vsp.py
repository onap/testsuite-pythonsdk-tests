from onapsdk.configuration import settings
from onapsdk.vendor import Vendor
from onapsdk.vsp import Vsp

from ..base import BaseComponent
from .vendor import VendorOnboardComponent


class VspOnboardComponent(BaseComponent):

    def __init__(self, cleanup=False):
        super().__init__(cleanup=cleanup)
        self.add_subcomponent(VendorOnboardComponent(cleanup=cleanup))

    def action(self):
        super().action()
        vendor: Vendor = Vendor(name=settings.VENDOR_NAME)
        vsp: Vsp = Vsp(name=settings.VSP_NAME, vendor=vendor, package=open(settings.VSP_FILE_PATH, "rb"))
        vsp.onboard()
