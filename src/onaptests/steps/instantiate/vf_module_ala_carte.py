import time
from typing import Iterable
from uuid import uuid4
from yaml import load

from onapsdk.aai.business import Customer, ServiceInstance, ServiceSubscription
from onapsdk.configuration import settings
from onapsdk.sdc.service import Service
from onapsdk.so.instantiation import VnfParameter

from ..base import YamlTemplateBaseStep
from .vnf_ala_carte import YamlTemplateVnfAlaCarteInstantiateStep


class YamlTemplateVfModuleAlaCarteInstantiateStep(YamlTemplateBaseStep):

    def __init__(self, cleanup=False):
        super().__init__(cleanup=cleanup)
        self._yaml_template: dict = None
        self.add_step(YamlTemplateVnfAlaCarteInstantiateStep(cleanup))

    @property
    def yaml_template(self) -> dict:
        if self.is_root:
            if not self._yaml_template:
                with open(settings.SERVICE_YAML_TEMPLATE, "r") as yaml_template:
                    self._yaml_template: dict = load(yaml_template)
            return self._yaml_template
        return self.parent.yaml_template

    @property
    def service_name(self) -> str:
        if self.is_root:
            return next(iter(self.yaml_template.keys()))
        return self.parent.service_name

    @property
    def service_instance_name(self) -> str:
        if self.is_root:
            return f"{self.service_name}-{str(uuid4())}"
        return self.parent.service_instance_name

    def get_vnf_parameters(self, vnf_name: str) -> Iterable[VnfParameter]:
        for vnf in self.yaml_template[self.service_name]["vnfs"]:
            if vnf["vnf_name"] == vnf_name:
                for vnf_parameter in vnf["vnf_parameters"]:
                    yield VnfParameter(
                        name=vnf_parameter["name"],
                        value=vnf_parameter["value"]
                    )

    def execute(self) -> None:
        super().execute()
        customer: Customer = Customer.get_by_global_customer_id(settings.GLOBAL_CUSTOMER_ID)
        service_subscription: ServiceSubscription = customer.get_service_subscription_by_service_type(self.service_name)
        service_instance: ServiceInstance = service_subscription.get_service_instance_by_name(self.service_instance_name)
        for vnf_instance in service_instance.vnf_instances:
            vf_module_instantiation = vnf_instance.add_vf_module(
                vnf_instance.vnf.vf_module,
                vnf_parameters= self.get_vnf_parameters(vnf_instance.vnf.vnf_name))
            while not vf_module_instantiation.finished:
                time.sleep(10)
            if vf_module_instantiation.failed:
                raise Exception("Vf module instantiation failed")
