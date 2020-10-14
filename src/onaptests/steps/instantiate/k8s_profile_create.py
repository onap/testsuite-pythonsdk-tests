from typing import Iterable
from uuid import uuid4
from yaml import load

from onapsdk.aai.business import Customer, ServiceInstance, ServiceSubscription
from onapsdk.configuration import settings
from onapsdk.msb.k8s import Definition
from onapsdk.so.instantiation import VnfParameter

from ..base import BaseStep
from .vnf_ala_carte import YamlTemplateVnfAlaCarteInstantiateStep

class K8SProfileStep(BaseStep):
    """CreateK8sProfileStep."""

    def __init__(self, cleanup=False):
        """Initialize step.
        """
        super().__init__(cleanup=cleanup)

        self._yaml_template: dict = None
        self._service_instance_name: str = None
        self._service_instance: ServiceInstance = None
        self.add_step(YamlTemplateVnfAlaCarteInstantiateStep(cleanup))

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

    @BaseStep.store_state
    def execute(self):
        """Creation of k8s profile for resource bundle definition

        Use settings values:
         - GLOBAL_CUSTOMER_ID
         - K8S_PROFILE_K8S_VERSION
         - K8S_PROFILE_ARTIFACT_PATH.
        """
        super().execute()
        customer: Customer = Customer.get_by_global_customer_id(settings.GLOBAL_CUSTOMER_ID)
        service_subscription: ServiceSubscription = customer.get_service_subscription_by_service_type(self.service_name)
        self._service_instance: ServiceInstance = service_subscription.get_service_instance_by_name(self.service_instance_name)

        for vnf_instance in self._service_instance.vnf_instances:
            # possible to have several modules for 1 VNF
            for vf_module in vnf_instance.vnf.vf_modules:
                # Define profile (rb_profile) for resource bundle definition
                # Retrieve resource bundle definition (rbdef) corresponding to vf module
                rbdef_name = vf_module.metadata["vfModuleModelInvariantUUID"]
                rbdef_version = vf_module.metadata["vfModuleModelUUID"]
                rbdef = Definition.get_definition_by_name_version(rbdef_name, rbdef_version)
                # Get k8s profile name from yaml service template
                vnf_parameters = self.get_vnf_parameters(vnf_instance.vnf.name)
                k8s_profile_name = ""
                k8s_profile_namespace = ""
                for param in vnf_parameters:
                    if param.name == "k8s-rb-profile-name":
                        k8s_profile_name = param.value
                    if param.name == "k8s-rb-profile-namespace":
                        k8s_profile_namespace = param.value
                if k8s_profile_name == "" or k8s_profile_namespace == "":
                    raise Exception("Vf module instantiation failed, missing rb profile information")
                ######## Check profile for Definition ###################################
                try:
                    rbdef.get_profile_by_name(k8s_profile_name)
                except ValueError:
                    ######## Create profile for Definition ###################################
                    profile = rbdef.create_profile(k8s_profile_name,
                                                   k8s_profile_namespace,
                                                   settings.K8S_PROFILE_K8S_VERSION)
                    ####### Upload artifact for created profile ##############################
                    profile.upload_artifact(open(settings.K8S_PROFILE_ARTIFACT_PATH, 'rb').read())

    def cleanup(self) -> None:
        """Cleanup K8S profiles.
        """
        self._logger.info("*Clean the k8s profile *")
        for vnf_instance in self._service_instance.vnf_instances:
            # possible to have several modules for 1 VNF
            for vf_module in vnf_instance.vnf.vf_modules:
                # Retrieve resource bundle definition (rbdef) corresponding to vf module
                rbdef_name = vf_module.metadata["vfModuleModelInvariantUUID"]
                rbdef_version = vf_module.metadata["vfModuleModelUUID"]
                rbdef = Definition.get_definition_by_name_version(rbdef_name, rbdef_version)
                # Get k8s profile name from yaml service template
                vnf_parameters = self.get_vnf_parameters(vnf_instance.vnf.name)
                k8s_profile_name = ""
                for param in vnf_parameters:
                    if param.name == "k8s-rb-profile-name":
                        k8s_profile_name = param.value
                if k8s_profile_name == "":
                    raise Exception("K8s profile deletion failed, missing rb profile name")
                ######## Delete profile for Definition ###################################
                try:
                    profile = rbdef.get_profile_by_name(k8s_profile_name)
                    profile.delete()
                except ValueError:
                    self._logger.error("K8s profile deletion %s failed", k8s_profile_name)
                    raise Exception("K8s profile deletion failed")
        super().cleanup()
