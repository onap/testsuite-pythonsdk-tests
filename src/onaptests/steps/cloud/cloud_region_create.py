from onapsdk.aai.cloud_infrastructure import CloudRegion
from onapsdk.configuration import settings

from ..base import BaseStep


class CloudRegionCreateStep(BaseStep):

    def execute(self):
        super().execute()
        CloudRegion.create(
            cloud_owner=settings.CLOUD_REGION_CLOUD_OWNER,
            cloud_region_id=settings.CLOUD_REGION_ID,
            orchestration_disabled=False,
            in_maint=False,
            cloud_type=settings.CLOUD_REGION_TYPE,
            cloud_region_version=settings.CLOUD_REGION_VERSION
        )
