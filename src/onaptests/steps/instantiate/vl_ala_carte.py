import re
from typing import Iterable
from uuid import uuid4
from yaml import load

from onapsdk.aai.business import Customer, ServiceInstance, ServiceSubscription
from onapsdk.configuration import settings
from onapsdk.so.instantiation import Subnet
from onapsdk.sdc.service import Service
from onapsdk.vid import LineOfBusiness, Platform

import onaptests.utils.exceptions as onap_test_exceptions
from ..base import YamlTemplateBaseStep
from .service_ala_carte import YamlTemplateServiceAlaCarteInstantiateStep


class YamlTemplateVlAlaCarteInstantiateStep(YamlTemplateBaseStep):
    """Instantiate vl a'la carte using YAML template."""

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
        return "Instantiate network link described in YAML using SO a'la carte method."

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

    def get_subnets(self, network_name: str) -> Iterable[Subnet]:
        """Get Network parameters from YAML template.

        Args:
            network_name (str): Network name to get parameters for.

        Yields:
            Iterator[Iterable[Subnet]]: Subnets

        """
        # workaround, as Network name differs from model name (added " 0")
        network_name=re.sub(r"\s\d$", r"", network_name)
        for net in self.yaml_template[self.service_name]["networks"]:
            if net["vl_name"] == network_name:
                if net['subnets'] is None:
                    print("No Subnet defined")
                else:
                    for subnet in net['subnets']:
                        yield Subnet(
                            name=subnet['subnet-name'],
                            start_address=subnet['start-address'],
                            gateway_address=subnet['gateway-address'],
                            cidr_mask=subnet['cidr-mask'],
                            ip_version=subnet['ip-version'],
                            dhcp_enabled=subnet['dhcp-enabled'])

    @YamlTemplateBaseStep.store_state
    def execute(self) -> None:
        """Instantiate Vl.

        Use settings values:
         - GLOBAL_CUSTOMER_ID.

        Raises:
            Exception: Vl instantiation failed

        """
        super().execute()
        service: Service = Service(self.service_name)
        customer: Customer = Customer.get_by_global_customer_id(settings.GLOBAL_CUSTOMER_ID)
        service_subscription: ServiceSubscription = customer.get_service_subscription_by_service_type(self.service_name)
        service_instance: ServiceInstance = service_subscription.get_service_instance_by_name(self.service_instance_name)
        self._service_instance = service_instance
        line_of_business: LineOfBusiness = LineOfBusiness(settings.LINE_OF_BUSINESS)
        platform: Platform = Platform(settings.PLATFORM)
        for idx, network in enumerate(service.networks):
        #for network in self.yaml_template[self.service_name]["networks"]:
            net_instantiation = service_instance.add_network(
                network,
                line_of_business,
                platform,
                network_instance_name=f"{self.service_instance_name}_net_{idx}",
                subnets=self.get_subnets(network.name))
            try:
                net_instantiation.wait_for_finish(settings.ORCHESTRATION_REQUEST_TIMEOUT)
                if net_instantiation.failed:
                    self._logger.error("VL instantiation %s failed", net_instantiation.name)
                    raise onap_test_exceptions.NetworkInstantiateException
            except TimeoutError:
                self._logger.error("VL instantiation %s timed out", net_instantiation.name)
                raise onap_test_exceptions.NetworkInstantiateException

    @YamlTemplateBaseStep.store_state(cleanup=True)
    def cleanup(self) -> None:
        """Cleanup VL.

        Raises:
            Exception: VL cleaning failed
        """
        if self._cleanup:
            for net_instance in self._service_instance.network_instances:
                self._logger.info("Start network deletion %s",net_instance.name)
                net_deletion = net_instance.delete(a_la_carte=True)
                try:
                    net_deletion.wait_for_finish(settings.ORCHESTRATION_REQUEST_TIMEOUT)
                    if net_deletion.failed:
                        self._logger.error("VL deletion %s failed", net_instance.name)
                        raise onap_test_exceptions.NetworkCleanupException
                except TimeoutError:
                    self._logger.error("VL deletion %s timed out", net_instance.name)
                    raise onap_test_exceptions.NetworkCleanupException
            super().cleanup()
