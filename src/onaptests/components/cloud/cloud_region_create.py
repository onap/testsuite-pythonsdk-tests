from onapsdk.aai.cloud_infrastructure import CloudRegion
from onapsdk.configuration import settings

from ..base import BaseComponent


class CloudRegionCreateComponent(BaseComponent):

    def action(self):
        super().action()
        CloudRegion.create(
            cloud_owner=settings.CLOUD_REGION_CLOUD_OWNER,
            cloud_region_id=settings.CLOUD_REGION_ID,
            orchestration_disabled=False,
            in_maint=False,
            cloud_type=settings.CLOUD_REGION_TYPE,
            cloud_region_version=settings.CLOUD_REGION_VERSION
        )
