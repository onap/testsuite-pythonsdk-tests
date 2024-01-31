from typing import Iterable
from uuid import uuid4

from onapsdk.aai.cloud_infrastructure import CloudRegion, Tenant
from onapsdk.configuration import settings
from onapsdk.so.instantiation import InstantiationParameter
from yaml import SafeLoader, load

import onaptests.utils.exceptions as onap_test_exceptions

from ..base import YamlTemplateBaseStep
from .k8s_profile_create import K8SProfileStep
from .vnf_ala_carte import YamlTemplateVnfAlaCarteInstantiateStep


class YamlTemplateVfModuleAlaCarteInstantiateStep(YamlTemplateBaseStep):
    """Instantiate vf module a'la carte using YAML template."""

    def __init__(self):
        """Initialize step.

        Substeps:
            - YamlTemplateVnfAlaCarteInstantiateStep.
        """
        super().__init__(cleanup=settings.CLEANUP_FLAG)

        self._yaml_template: dict = None
        self._service_instance_name: str = None
        if settings.CLOUD_REGION_TYPE == settings.K8S_REGION_TYPE:
            # K8SProfileStep creates the requested profile and then calls
            # YamlTemplateVnfAlaCarteInstantiateStep step
            self.add_step(K8SProfileStep())
        else:
            self.add_step(YamlTemplateVnfAlaCarteInstantiateStep())

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

    def get_vnf_parameters(self, vnf_name: str) -> Iterable[InstantiationParameter]:
        """Get VNF parameters from YAML template.

        Args:
            vnf_name (str): VNF name to get parameters for.

        Yields:
            Iterator[Iterable[InstantiationParameter]]: VNF parameter

        """

        # workaround, as VNF name differs from model name (added " 0")
        vnf_name = vnf_name.split()[0]
        for vnf in self.yaml_template[self.service_name]["vnfs"]:
            if vnf["vnf_name"] == vnf_name:
                for vnf_parameter in vnf["vnf_parameters"]:
                    yield InstantiationParameter(
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
        self._load_customer_and_subscription()
        self._load_service_instance()
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
                except TimeoutError as exc:
                    self._logger.error("VfModule instantiation %s timed out", vf_module.name)
                    raise onap_test_exceptions.VfModuleInstantiateException from exc

    @YamlTemplateBaseStep.store_state(cleanup=True)
    def cleanup(self) -> None:
        """Cleanup Vf module.

        Raises:
            Exception: Vf module cleaning failed

        """
        if self._service_instance:
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
                    except TimeoutError as exc:
                        self._logger.error("VfModule deletion %s timed out", vf_module.name)
                        raise onap_test_exceptions.VfModuleCleanupException from exc
        super().cleanup()
