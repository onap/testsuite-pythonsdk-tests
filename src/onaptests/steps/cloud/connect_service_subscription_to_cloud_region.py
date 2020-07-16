from onapsdk.aai.business import Customer, ServiceSubscription
from onapsdk.aai.cloud_infrastructure import CloudRegion, Tenant
from onapsdk.configuration import settings

from ..base import BaseStep
from .customer_service_subscription_create import CustomerServiceSubscriptionCreateStep
from .link_cloud_to_complex import LinkCloudRegionToComplexStep
from .register_cloud_to_multicloud import RegisterCloudRegionToMulticloudStep


class ConnectServiceSubToCloudRegionStep(BaseStep):

    def __init__(self, cleanup=False):
        super().__init__(cleanup=cleanup)
        self.add_step(LinkCloudRegionToComplexStep(cleanup=cleanup))
        self.add_step(RegisterCloudRegionToMulticloudStep(cleanup=cleanup))
        self.add_step(CustomerServiceSubscriptionCreateStep(cleanup=cleanup))

    def execute(self):
        super().execute()
        customer: Customer = Customer.get_by_global_customer_id(settings.GLOBAL_CUSTOMER_ID)
        service_subscription: ServiceSubscription = customer.get_service_subscription_by_service_type(settings.SERVICE_NAME)
        cloud_region: CloudRegion = CloudRegion.get_by_id(
            cloud_owner=settings.CLOUD_REGION_CLOUD_OWNER,
            cloud_region_id=settings.CLOUD_REGION_ID,
        )
        tenant: Tenant = cloud_region.get_tenant(settings.TENANT_ID)
        service_subscription.link_to_cloud_region_and_tenant(cloud_region=cloud_region, tenant=tenant)
