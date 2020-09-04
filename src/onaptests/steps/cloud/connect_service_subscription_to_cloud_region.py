from onapsdk.aai.business import Customer, ServiceSubscription
from onapsdk.aai.cloud_infrastructure import CloudRegion, Tenant
from onapsdk.configuration import settings

from ..base import BaseStep
from .customer_service_subscription_create import CustomerServiceSubscriptionCreateStep
from .link_cloud_to_complex import LinkCloudRegionToComplexStep
from .register_cloud_to_multicloud import RegisterCloudRegionToMulticloudStep


class ConnectServiceSubToCloudRegionStep(BaseStep):
    """Connect service subscription to cloud region step."""

    def __init__(self, cleanup=False):
        """Initialize step.

        Substeps:
            - LinkCloudRegionToComplexStep,
            - RegisterCloudRegionToMulticloudStep,
            - CustomerServiceSubscriptionCreateStep.

        """
        super().__init__(cleanup=cleanup)
        self.add_step(LinkCloudRegionToComplexStep(cleanup=cleanup))
        self.add_step(RegisterCloudRegionToMulticloudStep(cleanup=cleanup))
        self.add_step(CustomerServiceSubscriptionCreateStep(cleanup=cleanup))

    def execute(self):
        """Connect service subsription to cloud region and tenant.

        Use settings values:
         - GLOBAL_CUSTOMER_ID,
         - SERVICE_NAME,
         - CLOUD_REGION_CLOUD_OWNER,
         - CLOUD_REGION_ID.

        """
        super().execute()
        customer: Customer = Customer.get_by_global_customer_id(
            settings.GLOBAL_CUSTOMER_ID)
        service_subscription: ServiceSubscription = customer.get_service_subscription_by_service_type(
            settings.SERVICE_NAME)
        cloud_region: CloudRegion = CloudRegion.get_by_id(
            cloud_owner=settings.CLOUD_REGION_CLOUD_OWNER,
            cloud_region_id=settings.CLOUD_REGION_ID,
        )

        # Retrieve the tenant
        # if it does not exist, create it
        try:
            tenant: Tenant = cloud_region.get_tenant(settings.TENANT_ID)
        except ValueError:
            self._logger.warning("Impossible to retrieve the Specificed Tenant")
            self._logger.debug("If no multicloud selected, add the tenant")
            cloud_region.add_tenant(
                tenant_id=settings.TENANT_ID,
                tenant_name=settings.TENANT_NAME)

        # be sure that an availability zone has been created
        # if not, create it
        try:
            availability_zone: AvailabilityZone = cloud_region.get_availability_zone_by_name(
                settings.AVAILABILITY_ZONE_NAME)
        except ValueError:
            cloud_region.add_availability_zone(
                settings.AVAILABILITY_ZONE_NAME,
                settings.AVAILABILITY_ZONE_TYPE)

        # retrieve tenant
        # for which we are sure that an availability zone has been created
        tenant: Tenant = cloud_region.get_tenant(settings.TENANT_ID)

        service_subscription.link_to_cloud_region_and_tenant(cloud_region=cloud_region, tenant=tenant)
