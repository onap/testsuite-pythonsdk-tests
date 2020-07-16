import time
from uuid import uuid4
from yaml import load

from onapsdk.aai.cloud_infrastructure import CloudRegion, Tenant
from onapsdk.aai.business import Customer
from onapsdk.aai.business.owning_entity import OwningEntity as AaiOwningEntity
from onapsdk.configuration import settings
from onapsdk.sdc.service import Service
from onapsdk.so.instantiation import ServiceInstantiation
from onapsdk.vid import Project

from ..base import BaseStep, YamlTemplateBaseStep
from ..cloud.connect_service_subscription_to_cloud_region import ConnectServiceSubToCloudRegionStep
from ..onboard.service import ServiceOnboardStep, YamlTemplateServiceOnboardStep


class ServiceAlaCarteInstantiateStep(BaseStep):

    def __init__(self, cleanup=False):
        super().__init__(cleanup=cleanup)
        self.add_step(ServiceOnboardStep(cleanup))
        self.add_step(ConnectServiceSubToCloudRegionStep(cleanup))

    def execute(self):
        super().execute()
        service = Service(settings.SERVICE_NAME)
        customer: Customer = Customer.get_by_global_customer_id(settings.GLOBAL_CUSTOMER_ID)
        cloud_region: CloudRegion = CloudRegion.get_by_id(
            cloud_owner=settings.CLOUD_REGION_CLOUD_OWNER,
            cloud_region_id=settings.CLOUD_REGION_ID,
        )
        tenant: Tenant = cloud_region.get_tenant(settings.TENANT_ID)
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


class YamlTemplateServiceAlaCarteInstantiateStep(YamlTemplateBaseStep):

    def __init__(self, cleanup=False):
        super().__init__(cleanup=cleanup)
        self._yaml_template: dict = None
        self.add_step(YamlTemplateServiceOnboardStep(cleanup))
        self.add_step(ConnectServiceSubToCloudRegionStep(cleanup))

    @property
    def yaml_template(self) -> dict:
        if self.is_root:
            if not self._yaml_template:
                with open(settings.SERVICE_YAML_TEMPLATE, "r") as yaml_template:
                    self._yaml_template: dict = load(yaml_template)
            return self._yaml_template
        return self.parent.yaml_template

    @property
    def service_name(self) -> str:
        if self.is_root:
            return next(iter(self.yaml_template.keys()))
        return self.parent.service_name

    @property
    def name(self) -> str:
        if self.is_root:
            return f"{self.service_name}-{str(uuid4())}"
        return self.parent.service_instance_name

    def execute(self):
        super().execute()
        service = Service(self.service_name)
        customer: Customer = Customer.get_by_global_customer_id(settings.GLOBAL_CUSTOMER_ID)
        cloud_region: CloudRegion = CloudRegion.get_by_id(
            cloud_owner=settings.CLOUD_REGION_CLOUD_OWNER,
            cloud_region_id=settings.CLOUD_REGION_ID,
        )
        tenant: Tenant = cloud_region.get_tenant(settings.TENANT_ID)
        owning_entity = AaiOwningEntity.get_by_owning_entity_name(settings.OWNING_ENTITY)
        vid_project = Project.create(settings.PROJECT)

        service_instantiation = ServiceInstantiation.instantiate_so_ala_carte(
            service,
            cloud_region,
            tenant,
            customer,
            owning_entity,
            vid_project,
            service_instance_name=self.name
        )
        while not service_instantiation.finished:
            time.sleep(10)
        if service_instantiation.failed:
            raise Exception("Service instantiation failed")
