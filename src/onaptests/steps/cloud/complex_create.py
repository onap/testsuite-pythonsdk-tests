from onapsdk.aai.cloud_infrastructure import Complex
from onapsdk.configuration import settings

from ..base import BaseStep


class ComplexCreateStep(BaseStep):
    """Complex creation step."""

    @BaseStep.store_state
    def execute(self):
        """Create complex.

        Use settings values:
         - COMPLEX_PHYSICAL_LOCATION_ID,
         - COMPLEX_DATA_CENTER_CODE.

        """
        super().execute()
        Complex.create(
            physical_location_id=settings.COMPLEX_PHYSICAL_LOCATION_ID,
            data_center_code=settings.COMPLEX_DATA_CENTER_CODE,
            name=settings.COMPLEX_PHYSICAL_LOCATION_ID
        )
