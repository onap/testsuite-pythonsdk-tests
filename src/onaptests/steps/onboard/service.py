from typing import Any, Dict
from yaml import SafeLoader, load

from onapsdk.configuration import settings
from onapsdk.exceptions import ResourceNotFound
from onapsdk.sdc2.pnf import Pnf
from onapsdk.sdc2.component_instance import ComponentInstance, ComponentInstanceInput
from onapsdk.sdc2.sdc_resource import LifecycleOperation, LifecycleState
from onapsdk.sdc2.service import Service, ServiceInstantiationType
from onapsdk.sdc2.vf import Vf
from onapsdk.sdc2.vl import Vl

from ..base import BaseStep, YamlTemplateBaseStep
from .pnf import PnfOnboardStep, YamlTemplatePnfOnboardStep
from .vf import VfOnboardStep, YamlTemplateVfOnboardStep


class ServiceOnboardStep(BaseStep):
    """Service onboard step."""

    def __init__(self):
        """Initialize step.

        Substeps:
            - VfOnboardStep.
        """
        super().__init__(cleanup=settings.CLEANUP_FLAG)
        if settings.VF_NAME != "":
            self.add_step(VfOnboardStep())
        if settings.PNF_NAME != "":
            self.add_step(PnfOnboardStep())

    @property
    def description(self) -> str:
        """Step description."""
        return "Onboard service in SDC."

    @property
    def component(self) -> str:
        """Component name."""
        return "SDC"

    def check_preconditions(self, cleanup=False) -> bool:
        if not super().check_preconditions(cleanup):
            return False
        if cleanup:
            return settings.SDC_CLEANUP
        return True

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
        try:
            service: Service = Service.get_by_name(name=settings.SERVICE_NAME)
            if service.distributed:
                return
        except ResourceNotFound:
            service = Service.create(name=settings.SERVICE_NAME,
                                     instantiation_type=settings.SERVICE_INSTANTIATION_TYPE)
            if settings.VL_NAME != "":
                vl: Vl = Vl(name=settings.VL_NAME)
                service.add_resource(vl)
            if settings.VF_NAME != "":
                vf: Vf = Vf(name=settings.VF_NAME)
                service.add_resource(vf)
            if settings.PNF_NAME != "":
                pnf: Pnf = Pnf(name=settings.PNF_NAME)
                service.add_resource(pnf)
        if service.lifecycle_state != LifecycleState.CERTIFIED:
            service.lifecycle_operation(LifecycleOperation.CERTIFY)
        service.distribute()

    @BaseStep.store_state
    def cleanup(self) -> None:
        """Cleanup service onboard step."""
        try:
            service: Service = Service.get_by_name(name=settings.SERVICE_NAME)
            try:
                service.archive()
            except Exception:
                self._logger.warning(f"Service {settings.SERVICE_NAME} archive failed")
            service.delete()
        except ResourceNotFound:
            self._logger.info(f"Service {settings.SERVICE_NAME} not found")
        super().cleanup()


class YamlTemplateServiceOnboardStep(YamlTemplateBaseStep):
    """Service onboard using YAML template step."""

    def __init__(self):
        """Initialize step.

        Substeps:
            - YamlTemplateVfOnboardStep.
        """
        super().__init__(cleanup=settings.CLEANUP_FLAG)
        self._yaml_template: dict = None
        self._model_yaml_template: dict = None
        if "vnfs" in self.yaml_template[self.service_name]:
            self.add_step(YamlTemplateVfOnboardStep())
        if "pnfs" in self.yaml_template[self.service_name]:
            self.add_step(YamlTemplatePnfOnboardStep())

    @property
    def description(self) -> str:
        """Step description."""
        return "Onboard service described in YAML file in SDC."

    @property
    def component(self) -> str:
        """Component name."""
        return "SDC"

    def check_preconditions(self, cleanup=False) -> bool:
        if not super().check_preconditions(cleanup):
            return False
        if cleanup:
            return settings.SDC_CLEANUP
        return True

    @property
    def yaml_template(self) -> dict:
        """Step YAML template.

        Load from file if it's a root step, get from parent otherwise.

        Returns:
            dict: Step YAML template

        """
        if settings.MODEL_YAML_TEMPLATE:
            return self.model_yaml_template
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

    @YamlTemplateBaseStep.store_state
    def execute(self):
        """Onboard service."""
        super().execute()
        if "instantiation_type" in self.yaml_template[self.service_name]:
            instantiation_type: ServiceInstantiationType = ServiceInstantiationType(
                self.yaml_template[self.service_name]["instantiation_type"])
        else:
            instantiation_type: ServiceInstantiationType = ServiceInstantiationType.A_LA_CARTE
        try:
            service: Service = Service.get_by_name(name=self.service_name)
            if service.distributed:
                return
        except ResourceNotFound:
            service = Service.create(name=self.service_name, instantiation_type=instantiation_type)
            self.declare_resources(service)
            self.assign_properties(service)
        if service.lifecycle_state != LifecycleState.CERTIFIED:
            service.lifecycle_operation(LifecycleOperation.CERTIFY)
        service.distribute()

    def declare_resources(self, service: Service) -> None:
        """Declare resources.

        Resources defined in YAML template are declared.

        Args:
            service (Service): Service object

        """
        if "networks" in self.yaml_template[self.service_name]:
            for net in self.yaml_template[self.service_name]["networks"]:
                vl: Vl = Vl.get_by_name(name=net['vl_name'])
                service.add_resource(vl)
        if "vnfs" in self.yaml_template[self.service_name]:
            for vnf in self.yaml_template[self.service_name]["vnfs"]:
                vf: Vf = Vf.get_by_name(name=vnf["vnf_name"])
                service.add_resource(vf)
        if "pnfs" in self.yaml_template[self.service_name]:
            for pnf in self.yaml_template[self.service_name]["pnfs"]:
                pnf_obj: Pnf = Pnf.get_by_name(name=pnf["pnf_name"])
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
                    vl_component: ComponentInstance = service.get_component_by_name(net['vl_name'])
                    self.assign_properties_to_component(vl_component, net["properties"])
        if "vnfs" in self.yaml_template[self.service_name]:
            for vnf in self.yaml_template[self.service_name]["vnfs"]:
                if "properties" in vnf:
                    vf_component: ComponentInstance = service.get_component_by_name(vnf["vnf_name"])
                    self.assign_properties_to_component(vf_component, vnf["properties"])
        if "pnfs" in self.yaml_template[self.service_name]:
            for pnf in self.yaml_template[self.service_name]["pnfs"]:
                if "properties" in pnf:
                    pnf_component: ComponentInstance = \
                        service.get_component_by_name(pnf["pnf_name"])
                    self.assign_properties_to_component(pnf_component, pnf["properties"])

    def assign_properties_to_component(self,
                                       component: ComponentInstance,
                                       component_properties: Dict[str, Any]) -> None:
        """Assign properties to component.

        Args:
            component (Component): Component to which properites are going to be assigned
            component_properties (Dict[str, Any]): Properties dictionary

        """
        for property_name, property_value in component_properties.items():
            prop: ComponentInstanceInput = component.get_input_by_name(property_name)
            prop.value = property_value

    @YamlTemplateBaseStep.store_state(cleanup=True)
    def cleanup(self) -> None:
        """Cleanup service onboard step."""
        try:
            service: Service = Service.get_by_name(name=self.service_name)
            try:
                service.archive()
            except Exception:
                self._logger.warning(f"Service {settings.SERVICE_NAME} archive failed")
            service.delete()
        except ResourceNotFound:
            self._logger.info(f"Service {self.service_name} not found")
        super().cleanup()
