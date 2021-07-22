from typing import Iterable
from uuid import uuid4
from yaml import load

from onapsdk.aai.cloud_infrastructure import CloudRegion, Tenant
from onapsdk.aai.business import Customer, ServiceInstance, ServiceSubscription
from onapsdk.configuration import settings
from onapsdk.so.instantiation import VnfParameter

import onaptests.utils.exceptions as onap_test_exceptions
from ..base import YamlTemplateBaseStep
from .vnf_ala_carte import YamlTemplateVnfAlaCarteInstantiateStep
from .k8s_profile_create import K8SProfileStep

class YamlTemplateVfModuleAlaCarteInstantiateStep(YamlTemplateBaseStep):
    """Instantiate vf module a'la carte using YAML template."""

    def __init__(self, cleanup=False):
        """Initialize step.

        Substeps:
            - YamlTemplateVnfAlaCarteInstantiateStep.
        """
        super().__init__(cleanup=cleanup)

        self._yaml_template: dict = None
        self._service_instance_name: str = None
        self._service_instance: ServiceInstance = None
        if settings.CLOUD_REGION_TYPE == settings.K8S_REGION_TYPE:
            # K8SProfileStep creates the requested profile and then calls
            # YamlTemplateVnfAlaCarteInstantiateStep step
            self.add_step(K8SProfileStep(cleanup))
        else:
            self.add_step(YamlTemplateVnfAlaCarteInstantiateStep(cleanup))

    @property
    def description(self) -> str:
        """Step description."""
        return "Instantiate VF module described in YAML using SO a'la carte method."

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

    def get_vnf_parameters(self, vnf_name: str) -> Iterable[VnfParameter]:
        """Get VNF parameters from YAML template.

        Args:
            vnf_name (str): VNF name to get parameters for.

        Yields:
            Iterator[Iterable[VnfParameter]]: VNF parameter

        """

        # workaround, as VNF name differs from model name (added " 0")
        vnf_name = vnf_name.split()[0]
        for vnf in self.yaml_template[self.service_name]["vnfs"]:
            if vnf["vnf_name"] == vnf_name:
                for vnf_parameter in vnf["vnf_parameters"]:
                    yield VnfParameter(
                        name=vnf_parameter["name"],
                        value=vnf_parameter["value"]
                    )

    @YamlTemplateBaseStep.store_state
    def execute(self) -> None:
        """Instantiate Vf module.

        Use settings values:
         - GLOBAL_CUSTOMER_ID.

        Raises:
            Exception: Vf module instantiation failed

        """
        super().execute()
        customer: Customer = Customer.get_by_global_customer_id(settings.GLOBAL_CUSTOMER_ID)
        service_subscription: ServiceSubscription = customer.get_service_subscription_by_service_type(self.service_name)
        self._service_instance: ServiceInstance = service_subscription.get_service_instance_by_name(self.service_instance_name)
        cloud_region: CloudRegion = CloudRegion.get_by_id(
            cloud_owner=settings.CLOUD_REGION_CLOUD_OWNER,
            cloud_region_id=settings.CLOUD_REGION_ID,
        )
        tenant: Tenant = cloud_region.get_tenant(settings.TENANT_ID)

        for vnf_instance in self._service_instance.vnf_instances:
            # possible to have several moduels for 1 VNF
            for vf_module in vnf_instance.vnf.vf_modules:
                vf_module_instantiation = vnf_instance.add_vf_module(
                    vf_module,
                    cloud_region,
                    tenant,
                    self._service_instance_name,
                    vnf_parameters=self.get_vnf_parameters(vnf_instance.vnf.name))
                try:
                    vf_module_instantiation.wait_for_finish(settings.ORCHESTRATION_REQUEST_TIMEOUT)
                    if vf_module_instantiation.failed:
                        self._logger.error("VfModule instantiation %s failed", vf_module.name)
                        raise onap_test_exceptions.VfModuleInstantiateException
                except TimeoutError:
                    self._logger.error("VfModule instantiation %s timed out", vf_module.name)
                    raise onap_test_exceptions.VfModuleInstantiateException

    @YamlTemplateBaseStep.store_state(cleanup=True)
    def cleanup(self) -> None:
        """Cleanup Vf module.

        Raises:
            Exception: Vf module cleaning failed

        """
        for vnf_instance in self._service_instance.vnf_instances:
            self._logger.debug("VNF instance %s found in Service Instance ",
                               vnf_instance.name)
            self._logger.info("Get VF Modules")
            for vf_module in vnf_instance.vf_modules:
                self._logger.info("Delete VF Module %s",
                                  vf_module.name)
                vf_module_deletion = vf_module.delete(a_la_carte=True)

                try:
                    vf_module_deletion.wait_for_finish(settings.ORCHESTRATION_REQUEST_TIMEOUT)
                    if vf_module_deletion.failed:
                        self._logger.error("VfModule deletion %s failed", vf_module.name)
                        raise onap_test_exceptions.VfModuleCleanupException
                    self._logger.info("VfModule %s deleted", vf_module.name)
                except TimeoutError:
                    self._logger.error("VfModule deletion %s timed out", vf_module.name)
                    raise onap_test_exceptions.VfModuleCleanupException
        super().cleanup()
