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
    """Instantiate service a'la carte."""

    def __init__(self, cleanup=False):
        """Initialize step.

        Substeps:
            - ServiceOnboardStep,
            - ConnectServiceSubToCloudRegionStep.
        """
        super().__init__(cleanup=cleanup)
        self.add_step(ServiceOnboardStep(cleanup))
        self.add_step(ConnectServiceSubToCloudRegionStep(cleanup))

    def execute(self):
        """Instantiate service.

        Use settings values:
         - SERVICE_NAME,
         - GLOBAL_CUSTOMER_ID,
         - CLOUD_REGION_CLOUD_OWNER,
         - CLOUD_REGION_ID,
         - TENANT_ID,
         - OWNING_ENTITY,
         - PROJECT,
         - SERVICE_INSTANCE_NAME.
        """
        super().execute()
        service = Service(settings.SERVICE_NAME)
        customer: Customer = Customer.get_by_global_customer_id(settings.GLOBAL_CUSTOMER_ID)
        cloud_region: CloudRegion = CloudRegion.get_by_id(
            cloud_owner=settings.CLOUD_REGION_CLOUD_OWNER,
            cloud_region_id=settings.CLOUD_REGION_ID,
        )
        tenant: Tenant = cloud_region.get_tenant(settings.TENANT_ID)
        try:
            owning_entity = AaiOwningEntity.get_by_owning_entity_name(
                settings.OWNING_ENTITY)
        except ValueError:
            self._logger.info("Owning entity not found, create it")
            owning_entity = AaiOwningEntity.create(settings.OWNING_ENTITY)
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
    """Instantiate service a'la carte using YAML template."""

    def __init__(self, cleanup=False):
        """Initialize step.

        Substeps:
            - YamlTemplateServiceOnboardStep,
            - ConnectServiceSubToCloudRegionStep.
        """
        super().__init__(cleanup=cleanup)
        self._yaml_template: dict = None
        self.add_step(YamlTemplateServiceOnboardStep(cleanup))
        self.add_step(ConnectServiceSubToCloudRegionStep(cleanup))

    @property
    def yaml_template(self) -> dict:
        """Step YAML template.

        Load from file if it's a root step, get from parent otherwise.

        Returns:
            dict: Step YAML template

        """
        if self.is_root:
            if not self._yaml_template:
                with open(settings.SERVICE_YAML_TEMPLATE, "r") as yaml_template:
                    self._yaml_template: dict = load(yaml_template)
            return self._yaml_template
        return self.parent.yaml_template

    @property
    def service_name(self) -> str:
        """Service name.

        Get from YAML template if it's a root step, get from parent otherwise.

        Returns:
            str: Service name

        """
        if self.is_root:
            return next(iter(self.yaml_template.keys()))
        return self.parent.service_name

    @property
    def service_instance_name(self) -> str:
        """Service instance name.

        Generate using `service_name` and `uuid4()` function if it's a root step,
            get from parent otherwise.

        Returns:
            str: Service instance name

        """
        if self.is_root:
            return f"{self.service_name}-{str(uuid4())}"
        return self.parent.service_instance_name

    def execute(self):
        """Instantiate service.

        Use settings values:
         - GLOBAL_CUSTOMER_ID,
         - CLOUD_REGION_CLOUD_OWNER,
         - CLOUD_REGION_ID,
         - TENANT_ID,
         - OWNING_ENTITY,
         - PROJECT.

        Raises:
            Exception: Service instantiation failed

        """
        super().execute()
        service = Service(self.service_name)
        customer: Customer = Customer.get_by_global_customer_id(settings.GLOBAL_CUSTOMER_ID)
        cloud_region: CloudRegion = CloudRegion.get_by_id(
            cloud_owner=settings.CLOUD_REGION_CLOUD_OWNER,
            cloud_region_id=settings.CLOUD_REGION_ID,
        )
        tenant: Tenant = cloud_region.get_tenant(settings.TENANT_ID)
        try:
            owning_entity = AaiOwningEntity.get_by_owning_entity_name(
                settings.OWNING_ENTITY)
        except ValueError:
            self._logger.info("Owning entity not found, create it")
            owning_entity = AaiOwningEntity.create(settings.OWNING_ENTITY)
        vid_project = Project.create(settings.PROJECT)

        service_instantiation = ServiceInstantiation.instantiate_so_ala_carte(
            service,
            cloud_region,
            tenant,
            customer,
            owning_entity,
            vid_project,
            service_instance_name=self.service_instance_name
        )
        while not service_instantiation.finished:
            time.sleep(10)
        if service_instantiation.failed:
            raise Exception("Service instantiation failed")
