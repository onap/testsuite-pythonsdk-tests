from onapsdk.aai.cloud_infrastructure import Complex
from onapsdk.configuration import settings

from ..base import BaseStep


class ComplexCreateStep(BaseStep):

    def execute(self):
        super().execute()
        Complex.create(
            physical_location_id=settings.COMPLEX_PHYSICAL_LOCATION_ID,
            data_center_code=settings.COMPLEX_DATA_CENTER_CODE,
            name=settings.COMPLEX_PHYSICAL_LOCATION_ID
        )
