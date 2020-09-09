import time
from uuid import uuid4

from onapsdk.aai.cloud_infrastructure import CloudRegion
from onapsdk.configuration import settings

from ..base import BaseStep
from .cloud_region_create import CloudRegionCreateStep


class RegisterCloudRegionToMulticloudStep(BaseStep):
    """Cloud region registration in multicloud step."""

    def __init__(self, cleanup=False):
        """Initialize step.

        Substeps:
            - CloudRegionCreateStep.
        """
        super().__init__(cleanup=cleanup)
        self.add_step(CloudRegionCreateStep(cleanup=cleanup))

    def execute(self):
        """Register cloud region in multicloud.

        Use settings values:
         - CLOUD_REGION_CLOUD_OWNER,
         - CLOUD_REGION_ID,
         - CLOUD_DOMAIN,
         - VIM_USERNAME,
         - VIM_PASSWORD,
         - VIM_SERVICE_URL,
         - TENANT_NAME.
        """
        super().execute()
        cloud_region = CloudRegion.get_by_id(
            cloud_owner=settings.CLOUD_REGION_CLOUD_OWNER,
            cloud_region_id=settings.CLOUD_REGION_ID,
        )
        cloud_region.add_esr_system_info(
            esr_system_info_id=str(uuid4()),
            user_name=settings.VIM_USERNAME,
            password=settings.VIM_PASSWORD,
            system_type="VIM",
            service_url=settings.VIM_SERVICE_URL,
            ssl_insecure=False,
            system_status="active",
            cloud_domain=settings.CLOUD_DOMAIN,
            default_tenant=settings.TENANT_NAME
        )
        cloud_region.register_to_multicloud()

        time.sleep(20)
        nb_try = 0
        nb_try_max = 3
        while nb_try < nb_try_max:
            if len(cloud_region.tenants) == 0:
                time.sleep(20)
            else:
                break
            nb_try += 1
