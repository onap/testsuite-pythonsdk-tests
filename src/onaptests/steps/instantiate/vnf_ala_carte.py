from uuid import uuid4
from yaml import load

from onapsdk.aai.cloud_infrastructure import CloudRegion, Tenant
from onapsdk.aai.business import Customer, ServiceInstance, ServiceSubscription
from onapsdk.configuration import settings
from onapsdk.sdc.service import Service
from onapsdk.vid import LineOfBusiness, Platform

import onaptests.utils.exceptions as onap_test_exceptions
from ..base import YamlTemplateBaseStep
from .service_ala_carte import YamlTemplateServiceAlaCarteInstantiateStep


class YamlTemplateVnfAlaCarteInstantiateStep(YamlTemplateBaseStep):
    """Instantiate vnf a'la carte using YAML template."""

    def __init__(self, cleanup=False):
        """Initialize step.

        Substeps:
            - YamlTemplateServiceAlaCarteInstantiateStep.
        """
        super().__init__(cleanup=cleanup)
        self._yaml_template: dict = None
        self._service_instance_name: str = None
        self._service_instance: ServiceInstance = None
        self.add_step(YamlTemplateServiceAlaCarteInstantiateStep(cleanup))

    @property
    def description(self) -> str:
        """Step description."""
        return "Instantiate vnf described in YAML using SO a'la carte method."

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
        """Instantiate vnf.

        Use settings values:
         - GLOBAL_CUSTOMER_ID,
         - LINE_OF_BUSINESS.

        Raises:
            Exception: VNF instantiation failed

        """
        super().execute()
        service: Service = Service(self.service_name)
        customer: Customer = Customer.get_by_global_customer_id(settings.GLOBAL_CUSTOMER_ID)
        service_subscription: ServiceSubscription = customer.get_service_subscription_by_service_type(self.service_name)
        self._service_instance: ServiceInstance = service_subscription.get_service_instance_by_name(self.service_instance_name)
        cloud_region: CloudRegion = CloudRegion.get_by_id(
            cloud_owner=settings.CLOUD_REGION_CLOUD_OWNER,
            cloud_region_id=settings.CLOUD_REGION_ID,
        )
        tenant: Tenant = cloud_region.get_tenant(settings.TENANT_ID)
        for idx, vnf in enumerate(service.vnfs):
            vnf_instantiation = self._service_instance.add_vnf(
                vnf,
                settings.LINE_OF_BUSINESS,
                settings.PLATFORM,
                cloud_region,
                tenant,
                f"{self.service_instance_name}_vnf_{idx}")
            try:
                vnf_instantiation.wait_for_finish(settings.ORCHESTRATION_REQUEST_TIMEOUT)
                if vnf_instantiation.failed:
                    self._logger.error("VNF instantiation %s failed", vnf.name)
                    raise onap_test_exceptions.VnfInstantiateException
            except TimeoutError:
                self._logger.error("VNF instantiation %s timed out", vnf.name)
                raise onap_test_exceptions.VnfInstantiateException

    @YamlTemplateBaseStep.store_state(cleanup=True)
    def cleanup(self) -> None:
        """Cleanup VNF.

        Raises:
            Exception: VNF cleaning failed

        """
        for vnf_instance in self._service_instance.vnf_instances:
            vnf_deletion = vnf_instance.delete(a_la_carte=True)

            try:
                vnf_deletion.wait_for_finish(settings.ORCHESTRATION_REQUEST_TIMEOUT)
                if vnf_deletion.failed:
                    self._logger.error("VNF deletion %s failed", vnf_instance.name)
                    raise onap_test_exceptions.VnfCleanupException
            except TimeoutError:
                self._logger.error("VNF deletion %s timed out", vnf_instance.name)
                raise onap_test_exceptions.VnfCleanupException
        super().cleanup()
