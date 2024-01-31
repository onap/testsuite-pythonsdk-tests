"""A&AI cloud region registstation module."""
import time
from uuid import uuid4

from onapsdk.aai.cloud_infrastructure import CloudRegion
from onapsdk.configuration import settings
from onapsdk.exceptions import ResourceNotFound

from onaptests.steps.cloud.cloud_region_create import CloudRegionCreateStep

from ..base import BaseStep


class RegisterCloudRegionStep(BaseStep):
    """Cloud region registration step."""

    def __init__(self) -> None:
        """Initialize step.

        Substeps:
            - CloudRegionCreateStep.
        """
        super().__init__(cleanup=BaseStep.HAS_NO_CLEANUP)
        self.add_step(CloudRegionCreateStep())

    @property
    def description(self) -> str:
        """Step description."""
        return "Register cloud region."

    @property
    def component(self) -> str:
        """Component name."""
        return "AAI"

    @BaseStep.store_state
    def execute(self):  # noqa
        """Register cloud region.

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
        cloud_region: CloudRegion = CloudRegion.get_by_id(
            cloud_owner=settings.CLOUD_REGION_CLOUD_OWNER,
            cloud_region_id=settings.CLOUD_REGION_ID)
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
        if settings.USE_MULTICLOUD:
            self._logger.info("*Multicloud registration *")
            cloud_region.register_to_multicloud()
            time.sleep(20)
            nb_try = 0
            nb_try_max = 3
            while nb_try < nb_try_max:
                try:
                    if not cloud_region.tenants:
                        self._logger.debug("No tenats available, check one more time")
                        time.sleep(20)
                    else:
                        break
                except ResourceNotFound:
                    self._logger.debug("No tenats available, check one more time")
                    time.sleep(20)
                nb_try += 1

        # Retrieve the tenant, created by multicloud registration
        # if it does not exist, create it
        try:
            cloud_region.get_tenant(settings.TENANT_ID)
        except ResourceNotFound:
            self._logger.warning("Impossible to retrieve the Specificed Tenant")
            self._logger.debug("If no multicloud selected, add the tenant, reraise otherwise")
            if not settings.USE_MULTICLOUD:
                cloud_region.add_tenant(
                    tenant_id=settings.TENANT_ID,
                    tenant_name=settings.TENANT_NAME)
            else:
                raise

        # be sure that an availability zone has been created
        # if not, create it
        try:
            cloud_region.get_availability_zone_by_name(
                settings.AVAILABILITY_ZONE_NAME)
        except ResourceNotFound:
            cloud_region.add_availability_zone(
                settings.AVAILABILITY_ZONE_NAME,
                settings.AVAILABILITY_ZONE_TYPE)
