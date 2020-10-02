import time
from uuid import uuid4

from onapsdk.aai.cloud_infrastructure import CloudRegion
from onapsdk.configuration import settings

from ..base import BaseStep


class RegisterCloudRegionStep(BaseStep):
    """Cloud region registration step."""

    @BaseStep.store_state
    def execute(self):
        """Register cloud region

        Use settings values:
         - CLOUD_REGION_CLOUD_OWNER,
         - CLOUD_REGION_ID,
         - CLOUD_DOMAIN,
         - CLOUD_REGION_VERSION,
         - CLOUD_OWNER_DEFINED_TYPE,
         - COMPLEX_PHYSICAL_LOCATION_ID,
         - VIM_USERNAME,
         - VIM_PASSWORD,
         - VIM_SERVICE_URL,
         - TENANT_NAME.
        """
        super().execute()
        self._logger.info("*Check if cloud region exists *")
        try:
            cloud_region: CloudRegion = CloudRegion.get_by_id(
                cloud_owner=settings.CLOUD_REGION_CLOUD_OWNER,
                cloud_region_id=settings.CLOUD_REGION_ID,
            )
        except ValueError:
            self._logger.info("*Create the cloud region *")
            cloud_region: CloudRegion = CloudRegion.create(
                cloud_owner=settings.CLOUD_REGION_CLOUD_OWNER,
                cloud_region_id=settings.CLOUD_REGION_ID,
                orchestration_disabled=False,
                in_maint=False,
                cloud_type=settings.CLOUD_REGION_TYPE,
                cloud_region_version=settings.CLOUD_REGION_VERSION,
                owner_defined_type=settings.CLOUD_OWNER_DEFINED_TYPE,
                complex_name=settings.COMPLEX_PHYSICAL_LOCATION_ID
                # cloud_extra_info=settings.CLOUD_EXTRA_INFO
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
            if settings.USE_MULTICLOUD:
                self._logger.info("*Multicloud registration *")
                cloud_region.register_to_multicloud()
                time.sleep(20)
                nb_try = 0
                nb_try_max = 3
                while nb_try < nb_try_max:
                    if not cloud_region.tenants:
                        time.sleep(20)
                    else:
                        break
                    nb_try += 1

            # Retrieve the tenant, created by multicloud registration
            # if it does not exist, create it
            try:
                cloud_region.get_tenant(settings.TENANT_ID)
            except ValueError:
                self._logger.warning("Impossible to retrieve the Specificed Tenant")
                self._logger.debug("If no multicloud selected, add the tenant")
                cloud_region.add_tenant(
                    tenant_id=settings.TENANT_ID,
                    tenant_name=settings.TENANT_NAME)

            # be sure that an availability zone has been created
            # if not, create it
            try:
                cloud_region.get_availability_zone_by_name(
                    settings.AVAILABILITY_ZONE_NAME)
            except ValueError:
                cloud_region.add_availability_zone(
                    settings.AVAILABILITY_ZONE_NAME,
                    settings.AVAILABILITY_ZONE_TYPE)
