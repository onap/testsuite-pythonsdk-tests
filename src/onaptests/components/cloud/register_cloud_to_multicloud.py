from uuid import uuid4

from onapsdk.aai.cloud_infrastructure import CloudRegion
from onapsdk.configuration import settings

from ..base import BaseComponent
from .cloud_region_create import CloudRegionCreateComponent


class RegisterCloudRegionToMulticloudComponent(BaseComponent):

    def __init__(self, cleanup=False):
        super().__init__(cleanup=cleanup)
        self.add_subcomponent(CloudRegionCreateComponent(cleanup=cleanup))

    def action(self):
        super().action()
        cloud_region = CloudRegion.get_by_id(
            cloud_owner=settings.CLOUD_REGION_CLOUD_OWNER,
            cloud_region_id=settings.CLOUD_REGION_ID,
        )
        cloud_region.add_esr_system_info(
            esr_system_info_id=str(uuid4()),
            user_name=settings.VIM_USERNAME,
            password=settings.VIM_PASSWORD,
            system_type=settings.CLOUD_REGION_TYPE,
            service_url=settings.VIM_SERVICE_URL,
            cloud_domain=settings.CLOUD_DOMAIN
        )
        cloud_region.register_to_multicloud()
