from onapsdk.configuration import settings
from onapsdk.vf import Vf
from onapsdk.vsp import Vsp

from ..base import BaseComponent
from .vsp import VspOnboardComponent


class VfOnboardComponent(BaseComponent):

    def __init__(self, cleanup=False):
        super().__init__(cleanup=cleanup)
        self.add_subcomponent(VspOnboardComponent(cleanup=cleanup))

    def action(self):
        super().action()
        vsp: Vsp = Vsp(name=settings.VSP_NAME)
        vf: Vf = Vf(name=settings.VF_NAME, vsp=vsp)
        vf.onboard()
