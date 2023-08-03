from onapsdk.aai.cloud_infrastructure import Complex
from onapsdk.configuration import settings
from onapsdk.exceptions import APIError

from ..base import BaseStep


class ComplexCreateStep(BaseStep):
    """Complex creation step."""

    def __init__(self):
        """Initialize step."""
        super().__init__(cleanup=BaseStep.HAS_NO_CLEANUP)

    @property
    def description(self) -> str:
        """Step description."""
        return "Create complex."

    @property
    def component(self) -> str:
        """Component name."""
        return "AAI"

    @BaseStep.store_state
    def execute(self):
        """Create complex.

        Use settings values:
         - COMPLEX_PHYSICAL_LOCATION_ID,
         - COMPLEX_DATA_CENTER_CODE.

        """
        super().execute()
        try:
            Complex.create(
                physical_location_id=settings.COMPLEX_PHYSICAL_LOCATION_ID,
                data_center_code=settings.COMPLEX_DATA_CENTER_CODE,
                name=settings.COMPLEX_PHYSICAL_LOCATION_ID)
        except APIError:
            self._logger.warn("Try to update the complex failed.")
