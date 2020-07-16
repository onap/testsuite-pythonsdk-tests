import time
from uuid import uuid4
from yaml import load

from onapsdk.aai.business import Customer, ServiceInstance, ServiceSubscription
from onapsdk.configuration import settings
from onapsdk.service import Service
from onapsdk.vid import LineOfBusiness, Platform

from ..base import YamlTemplateBaseStep
from .service_ala_carte import YamlTemplateServiceAlaCarteInstantiateStep


class YamlTemplateVnfAlaCarteInstantiateStep(YamlTemplateBaseStep):

    def __init__(self, cleanup=False):
        super().__init__(cleanup=cleanup)
        self._yaml_template: dict = None
        self.add_step(YamlTemplateServiceAlaCarteInstantiateStep(cleanup))

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

    def execute(self):
        super().execute()
        service: Service = Service(self.service_name)
        customer: Customer = Customer.get_by_global_customer_id(settings.GLOBAL_CUSTOMER_ID)
        service_subscription: ServiceSubscription = customer.get_service_subscription_by_service_type(self.service_name)
        service_instance: ServiceInstance = service_subscription.get_service_instance_by_name(self.service_instance_name)
        line_of_business: LineOfBusiness = LineOfBusiness(settings.LINE_OF_BUSINESS)
        platform: Platform = Platform(settings.PLATFORM)
        for idx, vnf in service.vnfs:
            vnf_instantiation = service_instance.add_vnf(vnf, line_of_business, platform, f"{self.service_instance_name}_vnf_{idx}")
            while not vnf_instantiation.finished:
                time.sleep(10)
            if vnf_instantiation.failed:
                raise Exception("Vnf instantiation failed")
