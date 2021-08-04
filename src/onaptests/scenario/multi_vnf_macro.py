"""Instantiate basic vm using SO macro flow."""
import logging
import time

import openstack
from onapsdk.aai.business import ServiceInstance, ServiceSubscription, Customer
from yaml import load

from onapsdk.configuration import settings
from onapsdk.exceptions import SDKException
from xtesting.core import testcase

from onaptests.steps.base import YamlTemplateBaseStep
from onaptests.steps.onboard.cds import CbaPublishStep
from onaptests.utils.exceptions import OnapTestException
from onaptests.steps.instantiate.service_macro import YamlTemplateServiceMacroInstantiateStep
import onaptests.utils.exceptions as onap_test_exceptions


class MultiVnfUbuntuMacroStep(YamlTemplateBaseStep):

    def __init__(self, cleanup=False):
        """Initialize step.

        Substeps:
            - CbaPublishStep
            - YamlTemplateServiceAlaCarteInstantiateStep.
        """
        super().__init__(cleanup=cleanup)
        self._yaml_template: dict = None
        self._model_yaml_template: dict = None
        self.add_step(CbaPublishStep(
            cleanup=settings.CLEANUP_FLAG
        ))
        self.add_step(YamlTemplateServiceMacroInstantiateStep(
            cleanup=settings.CLEANUP_FLAG
        ))

    @property
    def description(self) -> str:
        """Step description.

        Used for reports

        Returns:
            str: Step description

        """
        return "Multi VNF Ubuntu macro scenario step"

    @property
    def component(self) -> str:
        """Component name.

        Name of component which step is related with.
            Most is the name of ONAP component.

        Returns:
            str: Component name

        """
        return "PythonSDK-tests"

    @property
    def yaml_template(self) -> dict:
        """YAML template abstract property.

        Every YAML template step need to implement that property.

        Returns:
            dict: YAML template

        """
        if not self._yaml_template:
            with open(settings.SERVICE_YAML_TEMPLATE, "r") as yaml_template:
                self._yaml_template: dict = load(yaml_template)
        return self._yaml_template

    @property
    def model_yaml_template(self) -> dict:
        if not self._model_yaml_template:
            with open(settings.MODEL_YAML_TEMPLATE, "r") as model_yaml_template:
                self._model_yaml_template: dict = load(model_yaml_template)
        return self._model_yaml_template

    @property
    def service_name(self) -> str:
        """Service name.

        Get from YAML template.

        Returns:
            str: Service name

        """
        return next(iter(self.yaml_template.keys()))

    @property
    def service_instance_name(self) -> str:
        """Service instance name.

        Returns:
            str: Service instance name

        """
        return settings.SERVICE_INSTANCE_NAME

    @YamlTemplateBaseStep.store_state
    def execute(self) -> None:
        super().execute()
        self._logger.info("Verify multi-vnf scenario...")

        conn = openstack.connect(cloud=settings.TEST_CLOUD)
        customer: Customer = Customer.get_by_global_customer_id(settings.GLOBAL_CUSTOMER_ID)
        service_subscription: ServiceSubscription = customer.get_service_subscription_by_service_type(
            self.service_name)

        # Service Instance verifications
        service_instance: ServiceInstance = service_subscription.get_service_instance_by_name(
            self.service_instance_name)

        if service_instance.instance_name != self.service_instance_name:
            raise onap_test_exceptions.OnapTestException(f"service {self.service_instance_name} not found")

        # VNFs verifications
        for template_vnf in self.yaml_template[self.service_name]["vnfs"]:
            # find the name of the vnf from template
            vnf_name = list(filter(lambda param: param["name"] == "vnf_name", template_vnf["vnf_parameters"]))[0][
                "value"]

            service_instance_vnfs = list(
                filter(lambda vnf_instance: vnf_instance.vnf_name == vnf_name, service_instance.vnf_instances))
            # we should match only one VNF in AAI
            if len(service_instance_vnfs) != 1:
                raise onap_test_exceptions.OnapTestException(
                    f"{vnf_name} vnf expected: 1 , found: {str(len(service_instance_vnfs))}")

            service_instance_vnf = service_instance_vnfs[0]

            # VF Modules verifications
            for template_vnf_vfmodule in template_vnf["vf_module_parameters"]:
                vf_module_instance_name = f"{self.service_instance_name}_{template_vnf_vfmodule['vf_module_name']}"
                stack_data = conn.get_stack(vf_module_instance_name)
                service_instance_vnf_vfmodules = list(
                    filter(lambda vf_module: vf_module.vf_module_name == vf_module_instance_name,
                           service_instance_vnf.vf_modules))

                # We should match only one VF Module in AAI
                if len(service_instance_vnf_vfmodules) != 1:
                    raise onap_test_exceptions.OnapTestException(
                        f"{vf_module_instance_name}  vf-module expected 1, found  {len(service_instance_vnf_vfmodules)}")

                service_instance_vnf_vfmodule = service_instance_vnf_vfmodules[0]

                # Check if Base VF-Modules are stored as base in AAI
                if template_vnf_vfmodule['model_name'] == "base":
                    if not service_instance_vnf_vfmodule.is_base_vf_module:
                        raise onap_test_exceptions.OnapTestException("is_base_vf_module expected: true, found: false")
                else:
                    if service_instance_vnf_vfmodule.is_base_vf_module:
                        raise onap_test_exceptions.OnapTestException("is_base_vf_module expected: false, found: true")

                # Check if data in Openstack match the values passed in VF Module parameters
                stack_data = conn.get_stack(vf_module_instance_name)
                if stack_data is None:
                    raise onap_test_exceptions.OnapTestException(f"stack {vf_module_instance_name} not found")

                for template_vfmodule_param in template_vnf_vfmodule['parameters']:
                    template_param_key = template_vfmodule_param['name']
                    template_param_value = template_vfmodule_param['value']
                    if template_param_key in stack_data['parameters'].keys():
                        stack_value = stack_data['parameters'][template_param_key]
                        if stack_value != template_param_value:
                            raise onap_test_exceptions.OnapTestException(
                                f"stack parameter value {template_param_value} not found")
                    else:
                        raise onap_test_exceptions.OnapTestException(
                            f"stack parameter name {template_param_key} not found")


class MultiVnfUbuntuMacro(testcase.TestCase):
    """Instantiate Multi VNF Ubuntu macro."""

    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        """Init multi-vnf macro use case."""
        if "case_name" not in kwargs:
            kwargs["case_name"] = 'multi-vnf ubuntu macro'
        super().__init__(**kwargs)
        self.__logger.debug("Multi VNF Ubuntu macro init started")
        self.test = MultiVnfUbuntuMacro(cleanup=settings.CLEANUP_FLAG)

    def run(self):
        """Run Multi VNF Ubuntu macro test."""
        self.start_time = time.time()
        try:
            self.test.execute()
            self.test.cleanup()
            self.result = 100
        except OnapTestException as exc:
            self.result = 0
            self.__logger.error(exc.error_message)
        except SDKException:
            self.result = 0
            self.__logger.error("SDK Exception")
        finally:
            self.stop_time = time.time()

    def clean(self):
        """Generate report."""
        self.test.reports_collection.generate_report()
