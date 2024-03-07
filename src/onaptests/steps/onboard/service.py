import time
from typing import Any, Dict, Iterator
from urllib.parse import urlencode

import mysql.connector as mysql
from onapsdk.aai.service_design_and_creation import Model
from onapsdk.configuration import settings
from onapsdk.exceptions import InvalidResponse, ResourceNotFound
from onapsdk.sdc2.component_instance import (ComponentInstance,
                                             ComponentInstanceInput)
from onapsdk.sdc2.pnf import Pnf
from onapsdk.sdc2.sdc_resource import LifecycleOperation, LifecycleState
from onapsdk.sdc2.service import Service, ServiceInstantiationType
from onapsdk.sdc2.vf import Vf
from onapsdk.sdc2.vl import Vl
from onapsdk.so.catalog_db_adapter import CatalogDbAdapter
from yaml import SafeLoader, load

import onaptests.utils.exceptions as onap_test_exceptions
from onaptests.scenario.scenario_base import BaseScenarioStep
from onaptests.utils.kubernetes import KubernetesHelper

from ..base import BaseStep, YamlTemplateBaseStep
from .pnf import YamlTemplatePnfOnboardStep
from .vf import YamlTemplateVfOnboardStep


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
            if service.lifecycle_state == LifecycleState.CERTIFIED:
                service.archive()
            service.delete()
        except ResourceNotFound:
            self._logger.info(f"Service {self.service_name} not found")
        super().cleanup()


class VerifyServiceDistributionStep(BaseScenarioStep):
    """Service distribution check step."""

    def __init__(self):
        """Initialize step."""
        super().__init__(cleanup=BaseStep.HAS_NO_CLEANUP)
        self.add_step(ServiceDistributionWaitStep())
        for notified_module in settings.SDC_SERVICE_DISTRIBUTION_COMPONENTS:
            self.add_step(VerifyServiceDistributionStatusStep(
                notified_module=notified_module))
        if settings.IN_CLUSTER:
            self.add_step(VerifyServiceDistributionInSoStep())
            self.add_step(VerifyServiceDistributionInSdncStep())
        self.add_step(VerifyServiceDistributionInAaiStep())

    @property
    def description(self) -> str:
        """Step description."""
        return "Verify complete status of distribution"

    @property
    def component(self) -> str:
        """Component name."""
        return "SDC"


class BaseServiceDistributionComponentCheckStep(BaseStep):
    """Service distribution check step."""

    def __init__(self, component_name: str, break_on_error: bool = True):
        """Initialize step.

        Args:
            component_name (str): Name of tested component
            break_on_error (bool): If step breaks execution when failed
        """
        super().__init__(cleanup=BaseStep.HAS_NO_CLEANUP,
                         break_on_error=break_on_error)
        self.component_name = component_name
        self.service: Service = None

    @property
    def description(self) -> str:
        """Step description."""
        return f"Check service distribution in {self.component_name}."

    @property
    def component(self) -> str:
        """Component name."""
        return self.component_name

    def execute(self):
        """Check service distribution status."""
        super().execute()
        self.service = Service.get_by_name(name=settings.SERVICE_NAME)


class ServiceDistributionWaitStep(BaseServiceDistributionComponentCheckStep):
    """Service distribution wait step."""

    def __init__(self):
        """Initialize step."""
        super().__init__(component_name="SDC", break_on_error=False)

    @BaseStep.store_state
    def execute(self):
        """Wait for service distribution."""
        super().execute()
        # Before instantiating, be sure that the service has been distributed
        self._logger.info("******** Check Service Distribution *******")
        distribution_completed = False
        nb_try = 0
        while distribution_completed is False and \
                nb_try < settings.SERVICE_DISTRIBUTION_NUMBER_OF_TRIES:
            distribution_completed = self.service.distributed
            if distribution_completed is True:
                self._logger.info(
                    "Service Distribution for %s is sucessfully finished",
                    self.service.name)
                break
            self._logger.info(
                "Service Distribution for %s ongoing, Wait for %d s",
                self.service.name, settings.SERVICE_DISTRIBUTION_SLEEP_TIME)
            time.sleep(settings.SERVICE_DISTRIBUTION_SLEEP_TIME)
            nb_try += 1

        if distribution_completed is False:
            msg = f"Service Distribution for {self.service.name} failed after timeout!!"
            self._logger.error(msg)
            raise onap_test_exceptions.ServiceDistributionException(msg)


class VerifyServiceDistributionStatusStep(BaseServiceDistributionComponentCheckStep):
    """Check service distribution in SO step."""

    def __init__(self, notified_module: str):
        """Initialize step.

        Args:
            notified_module (str): Name of notified module
        """

        component_name = notified_module.split("-")[0].upper()
        super().__init__(component_name=component_name)
        self.component_id = notified_module

    @property
    def description(self) -> str:
        """Step description."""
        return f"Check service distribution in {self.component_name} \
{self.component_id}."

    @BaseStep.store_state
    def execute(self):
        """Check service distribution status."""
        super().execute()
        if not self.service.distributed:
            latest_distribution = self.service.latest_distribution
            for status in latest_distribution.distribution_status_list:
                if status.component_id == self.component_id and status.failed:
                    msg = f"Service {self.service.name} is not \
distributed into [{self.component_id}]: {status.error_reason}"
                    self._logger.error(msg)
                    raise onap_test_exceptions.ServiceDistributionException(msg)
        msg = f"Service {self.service.name} is distributed in SO and {self.component_id}."
        self._logger.info(msg)


class VerifyServiceDistributionInSoStep(BaseServiceDistributionComponentCheckStep):
    """Check service distribution in SO step."""

    def __init__(self):
        """Initialize step."""
        super().__init__(component_name="SO")

    @BaseStep.store_state
    def execute(self):
        """Check service distribution status."""
        super().execute()
        try:
            CatalogDbAdapter.get_service_info(self.service.uuid)
        except ResourceNotFound as e:
            msg = f"Service {self.service.name} is missing in SO."
            self._logger.error(msg)
            raise onap_test_exceptions.ServiceDistributionException(msg) from e
        except InvalidResponse:
            # looks like json returned by SO catalog DB adapter returns wrong json
            # but we don't care here. It is important to just know if service is there
            pass


class VerifyServiceDistributionInAaiStep(BaseServiceDistributionComponentCheckStep):
    """Check service distribution in AAI step."""

    class ModelWithGet(Model):
        """"Workaround to fix """

        @classmethod
        def get_all(cls,
                    invariant_id: str = None,
                    resource_version: str = None) -> Iterator["Model"]:
            """Get all models.

            Args:
                invariant_id (str): model invariant ID
                resource_version (str): object resource version

            Yields:
                Model: Model object

            """
            filter_parameters: dict = cls.filter_none_key_values(
                {"model-invariant-id": invariant_id,
                 "resource-version": resource_version}
            )
            url: str = f"{cls.get_all_url()}?{urlencode(filter_parameters)}"
            for model in cls.send_message_json("GET", "Get A&AI sdc models",
                                               url).get("model", []):
                yield Model(
                    invariant_id=model.get("model-invariant-id"),
                    model_type=model.get("model-type"),
                    resource_version=model.get("resource-version")
                )

    def __init__(self):
        """Initialize step."""
        BaseServiceDistributionComponentCheckStep.__init__(
            self, component_name="AAI")

    @BaseStep.store_state
    def execute(self):
        """Check service distribution status."""
        super().execute()
        try:
            aai_services = self.ModelWithGet.get_all(
                invariant_id=self.service.invariant_uuid)
            for aai_service in aai_services:
                self._logger.info(
                    f"Resolved {aai_service.invariant_id} aai service")
        except ResourceNotFound as e:
            msg = f"Service {self.service.name} is missing in AAI."
            self._logger.error(msg)
            raise onap_test_exceptions.ServiceDistributionException(msg) from e


class VerifyServiceDistributionInSdncStep(BaseServiceDistributionComponentCheckStep):
    """Check service distribution in SDNC step."""

    SDNC_DATABASE = "sdnctl"
    SDNC_DB_LOGIN = "login"
    SDNC_DB_PASSWORD = "password"

    def __init__(self):
        """Initialize step."""
        BaseServiceDistributionComponentCheckStep.__init__(
            self, component_name="SDNC")

    @BaseStep.store_state
    def execute(self):
        """Check service distribution status."""
        super().execute()
        login, password = KubernetesHelper.get_credentials_from_secret(
            settings.SDNC_SECRET_NAME, self.SDNC_DB_LOGIN, self.SDNC_DB_PASSWORD)
        conn = None
        try:
            conn = mysql.connect(
                database=self.SDNC_DATABASE,
                host=settings.SDNC_DB_PRIMARY_HOST,
                port=settings.SDNC_DB_PORT,
                user=login,
                password=password)
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM service_model WHERE service_uuid = '{self.service.uuid}';")
            cursor.fetchall()
            if cursor.rowcount <= 0:
                msg = "Service model is missing in SDNC."
                self._logger.error(msg)
                raise onap_test_exceptions.ServiceDistributionException(msg)
            self._logger.info("Service found in SDNC")
            cursor.close()
        except Exception as e:
            msg = f"Service {self.service.name} is missing in SDNC."
            raise onap_test_exceptions.ServiceDistributionException(msg) from e
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
