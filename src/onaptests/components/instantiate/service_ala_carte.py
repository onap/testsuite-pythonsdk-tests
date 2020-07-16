from onapsdk.aai.cloud_infrastructure import CloudRegion, Tenant
from onapsdk.aai.business import Customer
from onapsdk.aai.business.owning_entity import OwningEntity as AaiOwningEntity
from onapsdk.service import Service
from onapsdk.vid import LineOfBusiness, OwningEntity, Platform, Project
from onapsdk.so.instantiation import ServiceInstantiation
from onapsdk.configuration import settings

from ..base import BaseComponent
from ..cloud.connect_service_subscription_to_cloud_region import ConnectServiceSubToCloudRegionComponent
from ..onboard.service import ServiceOnboardComponent


class ServiceAlaCarteInstantiateComponent(BaseComponent):

    def __init__(self, cleanup=False):
        super().__init__(cleanup=cleanup)
        self.add_subcomponent(ServiceOnboardComponent(cleanup))
        self.add_subcomponent(ConnectServiceSubToCloudRegionComponent(cleanup))

    def action(self):
        super().action()
        service = Service(settings.SERVICE_NAME)
        customer: Customer = Customer.get_by_global_customer_id(settings.GLOBAL_CUSTOMER_ID)
        cloud_region: CloudRegion = CloudRegion.get_by_id(
            cloud_owner=settings.CLOUD_REGION_CLOUD_OWNER,
            cloud_region_id=settings.CLOUD_REGION_ID,
        )
        tenant: Tenant = cloud_region.get_tenant(settings.TENANT_ID)
        vid_owning_entity = OwningEntity.create(settings.OWNING_ENTITY)
        owning_entity = AaiOwningEntity.get_by_owning_entity_name(settings.OWNING_ENTITY)
        vid_project = Project.create(settings.PROJECT)

        service_instantiation = ServiceInstantiation.instantiate_so_ala_carte(
            service,
            cloud_region,
            tenant,
            customer,
            owning_entity,
            vid_project,
            service_instance_name=settings.SERVICE_INSTANCE_NAME
        )
        while not service_instantiation.finished:
            time.sleep(10)
