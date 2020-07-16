from onapsdk.aai.cloud_infrastructure import CloudRegion, Complex
from onapsdk.configuration import settings

from ..base import BaseStep
from .cloud_region_create import CloudRegionCreateStep
from .complex_create import ComplexCreateStep


class LinkCloudRegionToComplexStep(BaseStep):

    def __init__(self, cleanup=False):
        super().__init__(cleanup=cleanup)
        self.add_step(ComplexCreateStep(cleanup=cleanup))
        self.add_step(CloudRegionCreateStep(cleanup=cleanup))

    def execute(self):
        super().execute()
        cmplx = Complex(
            physical_location_id=settings.COMPLEX_PHYSICAL_LOCATION_ID,
            name=settings.COMPLEX_PHYSICAL_LOCATION_ID
        )
        cloud_region = CloudRegion.get_by_id(
            cloud_owner=settings.CLOUD_REGION_CLOUD_OWNER,
            cloud_region_id=settings.CLOUD_REGION_ID,
        )
        cloud_region.link_to_complex(cmplx)
