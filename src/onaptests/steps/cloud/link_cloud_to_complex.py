from onapsdk.aai.cloud_infrastructure import CloudRegion, Complex
from onaptests.configuration import settings

from ..base import BaseStep
from .complex_create import ComplexCreateStep


class LinkCloudRegionToComplexStep(BaseStep):
    """Link cloud region to complex step"""

    def __init__(self, cleanup=False):
        """Initialize step.

        Substeps:
            - ComplexCreateStep,
            - CloudRegionCreateStep.
        """
        super().__init__(cleanup=cleanup)
        self.add_step(ComplexCreateStep(cleanup=cleanup))

    @property
    def description(self) -> str:
        """Step description."""
        return "Connect cloud region with complex."

    @property
    def component(self) -> str:
        """Component name."""
        return "AAI"

    @BaseStep.store_state
    def execute(self):
        """Link cloud region to complex.

        Use settings values:
         - COMPLEX_PHYSICAL_LOCATION_ID,
         - CLOUD_REGION_CLOUD_OWNER,
         - CLOUD_REGION_ID.
        """
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
