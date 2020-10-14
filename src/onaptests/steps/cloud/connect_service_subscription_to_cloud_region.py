from onapsdk.aai.business import Customer, ServiceSubscription
from onapsdk.aai.cloud_infrastructure import CloudRegion, Tenant
from onapsdk.configuration import settings

from ..base import BaseStep
from .customer_service_subscription_create import CustomerServiceSubscriptionCreateStep
from .link_cloud_to_complex import LinkCloudRegionToComplexStep
from .register_cloud import RegisterCloudRegionStep
from .k8s_connectivity_info_create import K8SConnectivityInfoStep


class ConnectServiceSubToCloudRegionStep(BaseStep):
    """Connect service subscription to cloud region step."""

    def __init__(self, cleanup=False):
        """Initialize step.

        Substeps:
            - LinkCloudRegionToComplexStep,
            - RegisterCloudRegionStep,
            - CustomerServiceSubscriptionCreateStep.

        """
        super().__init__(cleanup=cleanup)
        if settings.CLOUD_REGION_TYPE == "k8s":
            self.add_step(K8SConnectivityInfoStep(cleanup=cleanup))
        self.add_step(RegisterCloudRegionStep(cleanup=cleanup))
        self.add_step(LinkCloudRegionToComplexStep(cleanup=cleanup))
        self.add_step(CustomerServiceSubscriptionCreateStep(cleanup=cleanup))

    @BaseStep.store_state
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

        # retrieve tenant
        # for which we are sure that an availability zone has been created
        tenant: Tenant = cloud_region.get_tenant(settings.TENANT_ID)

        service_subscription.link_to_cloud_region_and_tenant(cloud_region=cloud_region, tenant=tenant)
