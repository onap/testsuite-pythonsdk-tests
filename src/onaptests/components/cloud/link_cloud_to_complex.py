from onapsdk.aai.cloud_infrastructure import CloudRegion, Complex
from onapsdk.configuration import settings

from ..base import BaseComponent
from .cloud_region_create import CloudRegionCreateComponent
from .complex_create import ComplexCreateComponent


class LinkCloudRegionToComplexComponent(BaseComponent):

    def __init__(self, cleanup=False):
        super().__init__(cleanup=cleanup)
        self.add_subcomponent(ComplexCreateComponent(cleanup=cleanup))
        self.add_subcomponent(CloudRegionCreateComponent(cleanup=cleanup))

    def action(self):
        super().action()
        cmplx = Complex(
            physical_location_id=settings.COMPLEX_PHYSICAL_LOCATION_ID,
            name=settings.COMPLEX_PHYSICAL_LOCATION_ID
        )
        cloud_region = CloudRegion.get_by_id(
            cloud_owner=settings.CLOUD_REGION_CLOUD_OWNER,
            cloud_region_id=settings.CLOUD_REGION_ID,
        )
        cloud_region.link_to_complex(cmplx)
