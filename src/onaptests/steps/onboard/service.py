import time
from typing import Any, Dict
from yaml import load, SafeLoader

from onapsdk.configuration import settings
from onapsdk.exceptions import APIError, ResourceNotFound
from onapsdk.sdc.component import Component
from onapsdk.sdc.pnf import Pnf
from onapsdk.sdc.properties import ComponentProperty
from onapsdk.sdc.service import Service, ServiceInstantiationType
from onapsdk.sdc.vf import Vf
from onapsdk.sdc.vl import Vl

from ..base import BaseStep, YamlTemplateBaseStep
from .pnf import PnfOnboardStep, YamlTemplatePnfOnboardStep
from .vf import VfOnboardStep, YamlTemplateVfOnboardStep


class ServiceOnboardStep(BaseStep):
    """Service onboard step."""

    def __init__(self, cleanup=False):
        """Initialize step.

        Substeps:
            - VfOnboardStep.
        """
        super().__init__(cleanup=cleanup)
        if settings.VF_NAME != "":
            self.add_step(VfOnboardStep(cleanup=cleanup))
        if settings.PNF_NAME != "":
            self.add_step(PnfOnboardStep(cleanup=cleanup))

    @property
    def description(self) -> str:
        """Step description."""
        return "Onboard service in SDC."

    @property
    def component(self) -> str:
        """Component name."""
        return "SDC"

    @BaseStep.store_state
    def execute(self):
        """Onboard service.

        Use settings values:
         - VL_NAME,
         - VF_NAME,
         - PNF_NAME,
         - SERVICE_NAME,
         - SERVICE_INSTANTIATION_TYPE.

        """
        super().execute()
        service: Service = Service(name=settings.SERVICE_NAME, instantiation_type=settings.SERVICE_INSTANTIATION_TYPE)
        if not service.created():
            service.create()
            if settings.VL_NAME != "":
                vl: Vl = Vl(name=settings.VL_NAME)
                service.add_resource(vl)
            if settings.VF_NAME != "":
                vf: Vf = Vf(name=settings.VF_NAME)
                service.add_resource(vf)
            if settings.PNF_NAME != "":
                pnf: Pnf = Pnf(name=settings.PNF_NAME)
                service.add_resource(pnf)
        # If the service is already distributed, do not try to checkin/onboard (replay of tests)
        # checkin is done if needed
        # If service is replayed, no need to try to re-onboard the model
        if not service.distributed:
            time.sleep(10)
            service.checkin()
            service.onboard()


class YamlTemplateServiceOnboardStep(YamlTemplateBaseStep):
    """Service onboard using YAML template step."""

    def __init__(self, cleanup=False):
        """Initialize step.

        Substeps:
            - YamlTemplateVfOnboardStep.
        """
        super().__init__(cleanup=cleanup)
        self._yaml_template: dict = None
        self._model_yaml_template: dict = None
        if "vnfs" in self.yaml_template[self.service_name]:
            self.add_step(YamlTemplateVfOnboardStep(cleanup=cleanup))
        if "pnfs" in self.yaml_template[self.service_name]:
            self.add_step(YamlTemplatePnfOnboardStep(cleanup=cleanup))

    @property
    def description(self) -> str:
        """Step description."""
        return "Onboard service described in YAML file in SDC."

    @property
    def component(self) -> str:
        """Component name."""
        return "SDC"

    @property
    def yaml_template(self) -> dict:
        """Step YAML template.

        Load from file if it's a root step, get from parent otherwise.

        Returns:
            dict: Step YAML template

        """
        if settings.MODEL_YAML_TEMPLATE:
            return self.model_yaml_template
        elif self.is_root:
            if not self._yaml_template:
                with open(settings.SERVICE_YAML_TEMPLATE, "r") as yaml_template:
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
                with open(settings.MODEL_YAML_TEMPLATE, "r") as model_yaml_template:
                    self._model_yaml_template: dict = load(model_yaml_template)
            return self._model_yaml_template
        return self.parent.model_yaml_template

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

    @YamlTemplateBaseStep.store_state
    def execute(self):
        """Onboard service."""
        super().execute()
        if "instantiation_type" in self.yaml_template[self.service_name]:
            instantiation_type: ServiceInstantiationType = ServiceInstantiationType(
                self.yaml_template[self.service_name]["instantiation_type"])
        else:
            instantiation_type: ServiceInstantiationType = ServiceInstantiationType.A_LA_CARTE
        service: Service = Service(name=self.service_name, instantiation_type=instantiation_type)
        if not service.created():
            service.create()
            self.declare_resources(service)
            self.assign_properties(service)
            # If the service is already distributed, do not try to checkin/onboard (replay of tests)
            # checkin is done if needed
            # If service is replayed, no need to try to re-onboard the model
        if not service.distributed:
            try:
                service.checkin()
            except (APIError, ResourceNotFound):
                # Retry as checkin may be a bit long
                # Temp workaround to avoid internal race in SDC
                time.sleep(10)
                service.checkin()
            service.onboard()

    def declare_resources(self, service: Service) -> None:
        """Declare resources.

        Resources defined in YAML template are declared.

        Args:
            service (Service): Service object

        """
        if "networks" in self.yaml_template[self.service_name]:
            for net in self.yaml_template[self.service_name]["networks"]:
                vl: Vl = Vl(name=net['vl_name'])
                service.add_resource(vl)
        if "vnfs" in self.yaml_template[self.service_name]:
            for vnf in self.yaml_template[self.service_name]["vnfs"]:
                vf: Vf = Vf(name=vnf["vnf_name"])
                service.add_resource(vf)
        if "pnfs" in self.yaml_template[self.service_name]:
            for pnf in self.yaml_template[self.service_name]["pnfs"]:
                pnf_obj: Pnf = Pnf(name=pnf["pnf_name"])
                service.add_resource(pnf_obj)

    def assign_properties(self, service: Service) -> None:
        """Assign components properties.

        For each component set properties and it's value if are declared
            in YAML template.

        Args:
            service (Service): Service object

        """
        if "networks" in self.yaml_template[self.service_name]:
            for net in self.yaml_template[self.service_name]["networks"]:
                if "properties" in net:
                    vl: Vl = Vl(name=net['vl_name'])
                    vl_component: Component = service.get_component(vl)
                    self.assign_properties_to_component(vl_component, net["properties"])
        if "vnfs" in self.yaml_template[self.service_name]:
            for vnf in self.yaml_template[self.service_name]["vnfs"]:
                if "properties" in vnf:
                    vf: Vf = Vf(name=vnf["vnf_name"])
                    vf_component: Component = service.get_component(vf)
                    self.assign_properties_to_component(vf_component, vnf["properties"])
        if "pnfs" in self.yaml_template[self.service_name]:
            for pnf in self.yaml_template[self.service_name]["pnfs"]:
                if "properties" in pnf:
                    pnf_obj: Pnf = Pnf(name=pnf["pnf_name"])
                    pnf_component: Component = service.get_component(pnf_obj)
                    self.assign_properties_to_component(pnf_component, pnf["properties"])

    def assign_properties_to_component(self,
                                       component: Component,
                                       component_properties: Dict[str, Any]) -> None:
        """Assign properties to component.

        Args:
            component (Component): Component to which properites are going to be assigned
            component_properties (Dict[str, Any]): Properties dictionary

        """
        for property_name, property_value in component_properties.items():
            prop: ComponentProperty = component.get_property(property_name)
            prop.value = property_value
