from uuid import uuid4

from onapsdk.aai.business.owning_entity import OwningEntity as AaiOwningEntity
from onapsdk.aai.cloud_infrastructure import CloudRegion, Tenant
from onapsdk.configuration import settings
from onapsdk.exceptions import ResourceNotFound
from onapsdk.sdc.service import Service
from onapsdk.so.instantiation import ServiceInstantiation
from yaml import SafeLoader, load

import onaptests.utils.exceptions as onap_test_exceptions
from onaptests.steps.instantiate.sdnc_service import TestSdncStep

from ..base import YamlTemplateBaseStep
from ..cloud.connect_service_subscription_to_cloud_region import \
    ConnectServiceSubToCloudRegionStep
from ..onboard.service import (VerifyServiceDistributionStep,
                               YamlTemplateServiceOnboardStep)


class YamlTemplateServiceAlaCarteInstantiateStep(YamlTemplateBaseStep):
    """Instantiate service a'la carte using YAML template."""

    def __init__(self):
        """Initialize step.

        Substeps:
            - YamlTemplateServiceOnboardStep,
            - ConnectServiceSubToCloudRegionStep.
            - VerifyServiceDistributionStep
            - TestSdncStep
        """
        super().__init__(cleanup=settings.CLEANUP_FLAG)
        self._yaml_template: dict = None
        self._service_instance_name: str = None
        if not settings.ONLY_INSTANTIATE:
            self.add_step(YamlTemplateServiceOnboardStep())
            self.add_step(ConnectServiceSubToCloudRegionStep())
        self.add_step(VerifyServiceDistributionStep())
        self.add_step(TestSdncStep(full=False))

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
                with open(settings.SERVICE_YAML_TEMPLATE, "r", encoding="utf-8") as yaml_template:
                    self._yaml_template: dict = load(yaml_template, SafeLoader)
            return self._yaml_template
        return self.parent.yaml_template

    @property
    def model_yaml_template(self) -> dict:
        return {}

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
        self._load_customer_and_subscription()
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

        service_instantiation = ServiceInstantiation.instantiate_ala_carte(
            service,
            cloud_region,
            tenant,
            self._customer,
            owning_entity,
            settings.PROJECT,
            self._service_subscription,
            service_instance_name=self.service_instance_name
        )
        try:
            service_instantiation.wait_for_finish(settings.ORCHESTRATION_REQUEST_TIMEOUT)
        except TimeoutError as exc:
            self._logger.error("Service instantiation %s timed out", self.service_instance_name)
            raise onap_test_exceptions.ServiceCleanupException from exc
        if service_instantiation.failed:
            self._logger.error("Service instantiation %s failed", self.service_instance_name)
            raise onap_test_exceptions.ServiceInstantiateException
        self._load_customer_and_subscription(reload=True)
        self._load_service_instance()

    @YamlTemplateBaseStep.store_state(cleanup=True)
    def cleanup(self) -> None:
        """Cleanup Service.

        Raises:
            Exception: Service cleaning failed

        """
        self._load_customer_and_subscription()
        self._load_service_instance()
        if self._service_instance:
            service_deletion = self._service_instance.delete(a_la_carte=True)
            try:
                service_deletion.wait_for_finish(settings.ORCHESTRATION_REQUEST_TIMEOUT)
            except TimeoutError as exc:
                self._logger.error("Service deletion %s timed out", self._service_instance_name)
                raise onap_test_exceptions.ServiceCleanupException from exc
            if service_deletion.finished:
                self._logger.info("Service %s deleted", self._service_instance_name)
            else:
                self._logger.error("Service deletion %s failed", self._service_instance_name)
                raise onap_test_exceptions.ServiceCleanupException
        super().cleanup()
