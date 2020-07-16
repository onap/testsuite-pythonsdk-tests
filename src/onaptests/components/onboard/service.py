from onapsdk.configuration import settings
from onapsdk.service import Service
from onapsdk.vf import Vf

from ..base import BaseComponent
from .vf import VfOnboardComponent


class ServiceOnboardComponent(BaseComponent):

    def __init__(self, cleanup=False):
        super().__init__(cleanup=cleanup)
        self.add_subcomponent(VfOnboardComponent(cleanup=cleanup))

    def action(self):
        super().action()
        vf: Vf = Vf(name=settings.VF_NAME)
        service: Service = Service(name=settings.SERVICE_NAME, resources=[vf])
        service.onboard()