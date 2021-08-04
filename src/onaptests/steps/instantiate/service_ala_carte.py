import time
from uuid import uuid4
from yaml import load

from onapsdk.aai.cloud_infrastructure import CloudRegion, Tenant
from onapsdk.aai.business import Customer, ServiceInstance, ServiceSubscription
from onapsdk.aai.business.owning_entity import OwningEntity as AaiOwningEntity
from onapsdk.configuration import settings
from onapsdk.exceptions import ResourceNotFound
from onapsdk.sdc.service import Service
from onapsdk.so.instantiation import ServiceInstantiation
from onapsdk.vid import Project

import onaptests.utils.exceptions as onap_test_exceptions
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
        if not settings.ONLY_INSTANTIATE:
            self.add_step(ServiceOnboardStep(cleanup))
            self.add_step(ConnectServiceSubToCloudRegionStep(cleanup))

    @property
    def description(self) -> str:
        """Step description."""
        return "Instantiate service using SO a'la carte method."

    @property
    def component(self) -> str:
        """Component name."""
        return "SO"

    @BaseStep.store_state
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
        except ResourceNotFound:
            self._logger.info("Owning entity not found, create it")
            owning_entity = AaiOwningEntity.create(settings.OWNING_ENTITY)
        vid_project = Project(settings.PROJECT)

        service_instantiation = ServiceInstantiation.instantiate_so_ala_carte(
            service,
            cloud_region,
            tenant,
            customer,
            owning_entity,
            vid_project,
            service_instance_name=settings.SERVICE_INSTANCE_NAME
        )
        try:
            service_instantiation.wait_for_finish(settings.ORCHESTRATION_REQUEST_TIMEOUT)
        except TimeoutError:
            self._logger.error("Service instantiation %s timed out", self.service_instance_name)
            raise onap_test_exceptions.ServiceInstantiateException
        if service_instantiation.failed:
            self._logger.error("Service instantiation %s failed", self.service_instance_name)
            raise onap_test_exceptions.ServiceInstantiateException


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
        self._service_instance_name: str = None
        self._service_instance: str = None
        if not settings.ONLY_INSTANTIATE:
            self.add_step(YamlTemplateServiceOnboardStep(cleanup))
            self.add_step(ConnectServiceSubToCloudRegionStep(cleanup))

    @property
    def description(self) -> str:
        """Step description."""
        return "Instantiate service described in YAML using SO a'la carte method."

    @property
    def component(self) -> str:
        """Component name."""
        return "SO"

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
    def model_yaml_template(self) -> dict:
        return {}

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
            if not self._service_instance_name:
                self._service_instance_name: str = f"{self.service_name}-{str(uuid4())}"
            return self._service_instance_name
        return self.parent.service_instance_name

    @YamlTemplateBaseStep.store_state
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
        except ResourceNotFound:
            self._logger.info("Owning entity not found, create it")
            owning_entity = AaiOwningEntity.create(settings.OWNING_ENTITY)
        vid_project = Project(settings.PROJECT)

        # Before instantiating, be sure that the service has been distributed
        self._logger.info("******** Check Service Distribution *******")
        distribution_completed = False
        nb_try = 0
        nb_try_max = 10
        while distribution_completed is False and nb_try < nb_try_max:
            distribution_completed = service.distributed
            if distribution_completed is True:
                self._logger.info(
                "Service Distribution for %s is sucessfully finished",
                service.name)
                break
            self._logger.info(
                "Service Distribution for %s ongoing, Wait for 60 s",
                service.name)
            time.sleep(60)
            nb_try += 1

        if distribution_completed is False:
            self._logger.error(
                "Service Distribution for %s failed !!",service.name)
            raise onap_test_exceptions.ServiceDistributionException

        service_instantiation = ServiceInstantiation.instantiate_so_ala_carte(
            service,
            cloud_region,
            tenant,
            customer,
            owning_entity,
            vid_project,
            service_instance_name=self.service_instance_name
        )
        try:
            service_instantiation.wait_for_finish(settings.ORCHESTRATION_REQUEST_TIMEOUT)
        except TimeoutError:
            self._logger.error("Service instantiation %s timed out", self.service_instance_name)
            raise onap_test_exceptions.ServiceCleanupException
        if service_instantiation.failed:
            self._logger.error("Service instantiation %s failed", self.service_instance_name)
            raise onap_test_exceptions.ServiceInstantiateException
        else:
            service_subscription: ServiceSubscription = customer.get_service_subscription_by_service_type(self.service_name)
            self._service_instance: ServiceInstance = service_subscription.get_service_instance_by_name(self.service_instance_name)

    @YamlTemplateBaseStep.store_state(cleanup=True)
    def cleanup(self) -> None:
        """Cleanup Service.

        Raises:
            Exception: Service cleaning failed

        """
        service_deletion = self._service_instance.delete(a_la_carte=True)
        try:
            service_deletion.wait_for_finish(settings.ORCHESTRATION_REQUEST_TIMEOUT)
        except TimeoutError:
            self._logger.error("Service deletion %s timed out", self._service_instance_name)
            raise onap_test_exceptions.ServiceCleanupException
        if service_deletion.finished:
            self._logger.info("Service %s deleted", self._service_instance_name)
        else:
            self._logger.error("Service deletion %s failed", self._service_instance_name)
            raise onap_test_exceptions.ServiceCleanupException
        super().cleanup()
