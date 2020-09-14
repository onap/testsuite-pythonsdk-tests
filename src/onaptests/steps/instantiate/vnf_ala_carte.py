import time
from uuid import uuid4
from yaml import load

from onapsdk.aai.cloud_infrastructure import CloudRegion, Tenant
from onapsdk.aai.business import Customer, ServiceInstance, ServiceSubscription
from onapsdk.configuration import settings
from onapsdk.sdc.service import Service
from onapsdk.vid import LineOfBusiness, Platform

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
        line_of_business: LineOfBusiness = LineOfBusiness(settings.LINE_OF_BUSINESS)
        platform: Platform = Platform(settings.PLATFORM)
        cloud_region: CloudRegion = CloudRegion.get_by_id(
            cloud_owner=settings.CLOUD_REGION_CLOUD_OWNER,
            cloud_region_id=settings.CLOUD_REGION_ID,
        )
        tenant: Tenant = cloud_region.get_tenant(settings.TENANT_ID)
        for idx, vnf in enumerate(service.vnfs):
            vnf_instantiation = self._service_instance.add_vnf(
                vnf,
                line_of_business,
                platform,
                cloud_region,
                tenant,
                f"{self.service_instance_name}_vnf_{idx}")
            while not vnf_instantiation.finished:
                time.sleep(10)
            if vnf_instantiation.failed:
                raise Exception("Vnf instantiation failed")

    def cleanup(self) -> None:
        """Cleanup VNF.

        Raises:
            Exception: VNF cleaning failed

        """
        super().cleanup()

        for vnf_instance in self._service_instance.vnf_instances:
            vnf_deletion = vnf_instance.delete()
            nb_try = 0
            nb_try_max = 30

            while not vnf_deletion.finished and nb_try < nb_try_max:
                self._logger.info("Wait for vnf deletion")
                nb_try += 1
                time.sleep(15)
            if vnf_deletion.finished:
                self._logger.info("VNF %s deleted", vnf_instance.name)
            else:
                self._logger.error("VNF deletion %s failed", vnf_instance.name)
                raise Exception("VNF Cleanup failed")
