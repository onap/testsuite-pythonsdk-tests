
import time
from typing import List
from uuid import uuid4

from onapsdk.aai.business.owning_entity import OwningEntity
from onapsdk.aai.cloud_infrastructure.cloud_region import CloudRegion
from onapsdk.aai.cloud_infrastructure.tenant import Tenant
from onapsdk.configuration import settings
from onapsdk.exceptions import ResourceNotFound
from onapsdk.sdc.service import Service
from onapsdk.so.instantiation import (InstantiationParameter,
                                      ServiceInstantiation, SoService,
                                      VfmoduleParameters, VnfParameters)
from yaml import SafeLoader, load

import onaptests.utils.exceptions as onap_test_exceptions
from onaptests.steps.base import YamlTemplateBaseStep
from onaptests.steps.cloud.connect_service_subscription_to_cloud_region import \
    ConnectServiceSubToCloudRegionStep
from onaptests.steps.cloud.customer_service_subscription_create import \
    CustomerServiceSubscriptionCreateStep
from onaptests.steps.onboard.service import YamlTemplateServiceOnboardStep


class YamlTemplateServiceMacroInstantiateStep(YamlTemplateBaseStep):
    """Instantiate service a'la carte using YAML template."""

    def __init__(self):
        """Initialize step.

        Substeps:
            - YamlTemplateServiceOnboardStep,
            - ConnectServiceSubToCloudRegionStep,
            - CustomerServiceSubscriptionCreateStep.
        """
        super().__init__(cleanup=settings.CLEANUP_FLAG)
        self._yaml_template: dict = None
        self._model_yaml_template: dict = None
        self._service_instance_name: str = None
        if not settings.ONLY_INSTANTIATE:
            self.add_step(YamlTemplateServiceOnboardStep())

            if any(
                filter(lambda x: x in self.yaml_template[self.service_name].keys(),
                       ["vnfs", "networks"])):
                # can additionally contain "pnfs", no difference
                self.add_step(ConnectServiceSubToCloudRegionStep())
            else:  # only pnfs
                self.add_step(CustomerServiceSubscriptionCreateStep())

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
                with open(settings.SERVICE_YAML_TEMPLATE, "r", encoding="utf-8") as yaml_template:
                    self._yaml_template: dict = load(yaml_template, SafeLoader)
            return self._yaml_template
        return self.parent.yaml_template

    @property
    def model_yaml_template(self) -> dict:
        """Step Model YAML template.

        Load from file if it's a root step, get from parent otherwise.

        Returns:
            dict: Step YAML template

        """
        if self.is_root:
            if not self._model_yaml_template:
                with open(settings.MODEL_YAML_TEMPLATE, "r",
                          encoding="utf-8") as model_yaml_template:
                    self._model_yaml_template: dict = load(model_yaml_template, SafeLoader)
            return self._model_yaml_template
        return self.parent.model_yaml_template

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
    def execute(self):  # noqa
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
        if any(
                filter(lambda x: x in self.yaml_template[self.service_name].keys(),
                       ["vnfs", "networks"])):
            cloud_region: CloudRegion = CloudRegion.get_by_id(
                cloud_owner=settings.CLOUD_REGION_CLOUD_OWNER,
                cloud_region_id=settings.CLOUD_REGION_ID,
            )
            tenant: Tenant = cloud_region.get_tenant(settings.TENANT_ID)
        else:
            #  Only PNF is going to be instantiated so
            #  neither cloud_region nor tenant are needed
            cloud_region, tenant = None, None
        try:
            owning_entity = OwningEntity.get_by_owning_entity_name(
                settings.OWNING_ENTITY)
        except ResourceNotFound:
            self._logger.info("Owning entity not found, create it")
            owning_entity = OwningEntity.create(settings.OWNING_ENTITY)

        # Before instantiating, be sure that the service has been distributed
        self._logger.info("******** Check Service Distribution *******")
        distribution_completed = False
        nb_try = 0
        while distribution_completed is False and \
                nb_try < settings.SERVICE_DISTRIBUTION_NUMBER_OF_TRIES:
            distribution_completed = service.distributed
            if distribution_completed is True:
                self._logger.info(
                    "Service Distribution for %s is sucessfully finished",
                    service.name)
                break
            self._logger.info(
                "Service Distribution for %s ongoing, Wait for %d s",
                service.name, settings.SERVICE_DISTRIBUTION_SLEEP_TIME)
            time.sleep(settings.SERVICE_DISTRIBUTION_SLEEP_TIME)
            nb_try += 1

        if distribution_completed is False:
            self._logger.error(
                "Service Distribution for %s failed !!", service.name)
            raise onap_test_exceptions.ServiceDistributionException

        so_service = None
        vnf_params_list: List[VnfParameters] = []
        if settings.MODEL_YAML_TEMPLATE:
            so_data = self.yaml_template[self.service_name]
            so_service = SoService(vnfs=so_data.get("vnfs", []),
                                   subscription_service_type=so_data.get(
                                       'subscription_service_type'))
        else:
            for vnf_data in self.yaml_template[self.service_name].get("vnfs", []):
                vnf_params_list.append(VnfParameters(
                    vnf_data["vnf_name"],
                    [InstantiationParameter(name=parameter["name"],
                                            value=parameter["value"]) for parameter in
                     vnf_data.get("vnf_parameters", [])],
                    [VfmoduleParameters(vf_module_data["vf_module_name"],
                                        [InstantiationParameter(name=parameter["name"],
                                                                value=parameter["value"]) for
                                         parameter in vf_module_data.get("parameters", [])])
                     for vf_module_data in vnf_data.get("vf_module_parameters", [])]
                ))

        service_instantiation = ServiceInstantiation.instantiate_macro(
            sdc_service=service,
            customer=self._customer,
            owning_entity=owning_entity,
            project=settings.PROJECT,
            line_of_business=settings.LINE_OF_BUSINESS,
            platform=settings.PLATFORM,
            cloud_region=cloud_region,
            tenant=tenant,
            service_subscription=self._service_subscription,
            service_instance_name=self.service_instance_name,
            vnf_parameters=vnf_params_list,
            enable_multicloud=settings.USE_MULTICLOUD,
            so_service=so_service
        )
        try:
            service_instantiation.wait_for_finish(timeout=settings.ORCHESTRATION_REQUEST_TIMEOUT)
        except TimeoutError as exc:
            self._logger.error("Service instantiation %s timed out", self.service_instance_name)
            raise onap_test_exceptions.ServiceInstantiateException from exc
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
            service_deletion = self._service_instance.delete(a_la_carte=False)
            try:
                service_deletion.wait_for_finish(timeout=settings.ORCHESTRATION_REQUEST_TIMEOUT)
            except TimeoutError as exc:
                self._logger.error("Service deletion %s timed out", self._service_instance_name)
                raise onap_test_exceptions.ServiceCleanupException from exc
            if service_deletion.finished:
                self._logger.info("Service %s deleted", self._service_instance_name)
            else:
                self._logger.error("Service deletion %s failed", self._service_instance_name)
                raise onap_test_exceptions.ServiceCleanupException
        super().cleanup()
