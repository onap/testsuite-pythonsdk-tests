"""A&AI cloud region creation module."""
from onapsdk.aai.cloud_infrastructure import CloudRegion
from onapsdk.configuration import settings

from ..base import BaseStep


class CloudRegionCreateStep(BaseStep):
    """Cloud region creation step."""

    @property
    def description(self) -> str:
        """Step description."""
        return "Create cloud region."

    @property
    def component(self) -> str:
        """Component name."""
        return "AAI"

    @BaseStep.store_state
    def execute(self):
        """Create cloud region.

        Use settings values:
         - CLOUD_REGION_CLOUD_OWNER,
         - CLOUD_REGION_ID,
         - CLOUD_REGION_TYPE,
         - CLOUD_REGION_VERSION,
         - CLOUD_OWNER_DEFINED_TYPE,
         - COMPLEX_PHYSICAL_LOCATION_ID.

        """
        super().execute()
        self._logger.info("*Check if cloud region exists *")
        try:
            CloudRegion.get_by_id(
                cloud_owner=settings.CLOUD_REGION_CLOUD_OWNER,
                cloud_region_id=settings.CLOUD_REGION_ID,
            )
        except ValueError:
            CloudRegion.create(
                cloud_owner=settings.CLOUD_REGION_CLOUD_OWNER,
                cloud_region_id=settings.CLOUD_REGION_ID,
                orchestration_disabled=False,
                in_maint=False,
                cloud_type=settings.CLOUD_REGION_TYPE,
                cloud_region_version=settings.CLOUD_REGION_VERSION,
                owner_defined_type=settings.CLOUD_OWNER_DEFINED_TYPE,
                complex_name=settings.COMPLEX_PHYSICAL_LOCATION_ID
            )
