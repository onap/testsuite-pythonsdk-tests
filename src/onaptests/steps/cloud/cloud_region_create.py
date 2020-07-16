from onapsdk.aai.cloud_infrastructure import CloudRegion
from onapsdk.configuration import settings

from ..base import BaseStep


class CloudRegionCreateStep(BaseStep):
    """Cloud region creation step."""

    def execute(self):
        """Create cloud region.

        Use settings values:
         - CLOUD_REGION_CLOUD_OWNER,
         - CLOUD_REGION_ID,
         - CLOUD_REGION_TYPE,
         - CLOUD_REGION_VERSION.

        """
        super().execute()
        CloudRegion.create(
            cloud_owner=settings.CLOUD_REGION_CLOUD_OWNER,
            cloud_region_id=settings.CLOUD_REGION_ID,
            orchestration_disabled=False,
            in_maint=False,
            cloud_type=settings.CLOUD_REGION_TYPE,
            cloud_region_version=settings.CLOUD_REGION_VERSION
        )
