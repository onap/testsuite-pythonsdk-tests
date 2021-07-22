
import time
from typing import List
from uuid import uuid4
from onapsdk.aai.business.service import ServiceInstance
from yaml import load

from onapsdk.aai.business.customer import Customer, ServiceSubscription
from onapsdk.aai.business.owning_entity import OwningEntity
from onapsdk.aai.cloud_infrastructure.cloud_region import CloudRegion
from onapsdk.aai.cloud_infrastructure.tenant import Tenant
from onapsdk.configuration import settings
from onapsdk.exceptions import ResourceNotFound
from onapsdk.sdc.service import Service
from onapsdk.so.instantiation import InstantiationParameter, ServiceInstantiation, VfmoduleParameters, VnfParameters
from onapsdk.vid import LineOfBusiness, Platform, Project
from onaptests.steps.cloud.customer_service_subscription_create import CustomerServiceSubscriptionCreateStep

import onaptests.utils.exceptions as onap_test_exceptions
from onaptests.steps.base import YamlTemplateBaseStep
from onaptests.steps.onboard.service import YamlTemplateServiceOnboardStep
from onaptests.steps.cloud.connect_service_subscription_to_cloud_region import ConnectServiceSubToCloudRegionStep


class YamlTemplateServiceMacroInstantiateStep(YamlTemplateBaseStep):
    """Instantiate service a'la carte using YAML template."""

    def __init__(self, cleanup=False):
        """Initialize step.

        Substeps:
            - YamlTemplateServiceOnboardStep,
            - ConnectServiceSubToCloudRegionStep,
            - CustomerServiceSubscriptionCreateStep.
        """
        super().__init__(cleanup=cleanup)
        self._yaml_template: dict = None
        self._service_instance_name: str = None
        self._service_instance: str = None
        if not settings.ONLY_INSTANTIATE:
            self.add_step(YamlTemplateServiceOnboardStep(cleanup))

            if any(
                filter(lambda x: x in self.yaml_template[self.service_name].keys(),
                       ["vnfs", "networks"])):
                # can additionally contain "pnfs", no difference
                self.add_step(ConnectServiceSubToCloudRegionStep(cleanup))
            else:  # only pnfs
                self.add_step(CustomerServiceSubscriptionCreateStep(cleanup))


    @property
    def description(self) -> str:
        """Step description."""
        return "Instantiate service described in YAML using SO macro method."

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
        if any(
                filter(lambda x: x in self.yaml_template[self.service_name].keys(),
                       ["vnfs", "networks"])):
            cloud_region: CloudRegion = CloudRegion.get_by_id(
                cloud_owner=settings.CLOUD_REGION_CLOUD_OWNER,
                cloud_region_id=settings.CLOUD_REGION_ID,
            )
            tenant: Tenant = cloud_region.get_tenant(settings.TENANT_ID)
        else:
            cloud_region, tenant = None, None  # Only PNF is going to be instantiated so
                                               # neither cloud_region nor tenant are needed
        try:
            owning_entity = OwningEntity.get_by_owning_entity_name(
                settings.OWNING_ENTITY)
        except ResourceNotFound:
            self._logger.info("Owning entity not found, create it")
            owning_entity = OwningEntity.create(settings.OWNING_ENTITY)
        vid_project: Project = Project(settings.PROJECT)
        line_of_business: LineOfBusiness = LineOfBusiness(settings.LINE_OF_BUSINESS)
        platform: Platform = Platform(settings.PLATFORM)

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

        vnf_params_list: List[VnfParameters] = []
        for vnf_data in self.yaml_template[self.service_name].get("vnfs", []):
            vnf_params_list.append(VnfParameters(
                vnf_data["vnf_name"],
                [InstantiationParameter(name=parameter["name"], value=parameter["value"]) for parameter in vnf_data.get("vnf_parameters", [])],
                [VfmoduleParameters(vf_module_data["vf_module_name"],
                 [InstantiationParameter(name=parameter["name"], value=parameter["value"]) for parameter in vf_module_data.get("parameters", [])]) \
                     for vf_module_data in vnf_data.get("vf_module_parameters", [])]
            ))

        service_instantiation = ServiceInstantiation.instantiate_macro(
            service,
            customer=customer,
            owning_entity=owning_entity,
            project=vid_project,
            line_of_business=line_of_business,
            platform=platform,
            cloud_region=cloud_region,
            tenant=tenant,
            service_instance_name=self.service_instance_name,
            vnf_parameters=vnf_params_list,
            enable_multicloud=settings.USE_MULTICLOUD
        )
        try:
            service_instantiation.wait_for_finish(timeout=settings.ORCHESTRATION_REQUEST_TIMEOUT)
        except TimeoutError:
            self._logger.error("Service instantiation %s timed out", self.service_instance_name)
            raise onap_test_exceptions.ServiceInstantiateException
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
        if self._service_instance:
            service_deletion = self._service_instance.delete(a_la_carte=False)
            try:
                service_deletion.wait_for_finish(timeout=settings.ORCHESTRATION_REQUEST_TIMEOUT)
            except TimeoutError:
                self._logger.error("Service deletion %s timed out", self._service_instance_name)
                raise onap_test_exceptions.ServiceCleanupException
            if service_deletion.finished:
                self._logger.info("Service %s deleted", self._service_instance_name)
            else:
                self._logger.error("Service deletion %s failed", self._service_instance_name)
                raise onap_test_exceptions.ServiceCleanupException
        super().cleanup()
