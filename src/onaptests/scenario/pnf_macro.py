"""Instantiate service with PNF using SO macro flow."""
import logging
import time

from onapsdk.configuration import settings
from onapsdk.exceptions import SDKException
from onaptests.scenario.scenario_base import ScenarioBase
from onaptests.steps.base import YamlTemplateBaseStep
from onaptests.steps.instantiate.service_macro import \
    YamlTemplateServiceMacroInstantiateStep
from onaptests.steps.onboard.cds import CbaEnrichStep
from onaptests.steps.instantiate.pnf_register_ves import \
    SendPnfRegisterVesEvent
from onaptests.utils.exceptions import OnapTestException
from yaml import SafeLoader, load


class PnfMacroScenarioStep(YamlTemplateBaseStep):
    """Step created to run scenarion and generate report."""

    def __init__(self, cleanup=False):
        """Initialize step.

        Substeps:
            - YamlTemplateServiceAlaCarteInstantiateStep.
        """
        super().__init__(cleanup=cleanup)
        self._yaml_template: dict = None
        self.add_step(SendPnfRegisterVesEvent(
            cleanup=cleanup
        ))
        self.add_step(CbaEnrichStep(
            cleanup=cleanup
        ))
        self.add_step(YamlTemplateServiceMacroInstantiateStep(
            cleanup=cleanup
        ))

    @property
    def description(self) -> str:
        """Step description.

        Used for reports

        Returns:
            str: Step description

        """
        return "PNF macro scenario step"

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
                self._yaml_template: dict = load(yaml_template, SafeLoader)
        return self._yaml_template

    @property
    def model_yaml_template(self) -> dict:
        return {}

    @property
    def service_name(self) -> dict:
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


class PnfMacro(ScenarioBase):
    """Run PNF simulator and onboard then instantiate a service with PNF."""

    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        """Init Basic Network use case."""
        super().__init__('pnf_macro', **kwargs)
        self.test = PnfMacroScenarioStep(cleanup=settings.CLEANUP_FLAG)

    def run(self):
        """Run PNF macro test."""
        self.start_time = time.time()
        try:
            for test_phase in (self.test.execute, self.test.cleanup):
                try:
                    test_phase()
                    self.result += 50
                except OnapTestException as exc:
                    self.__logger.exception(exc.error_message)
                except SDKException:
                    self.__logger.exception("SDK Exception")
        finally:
            self.stop_time = time.time()

    def clean(self):
        """Generate report."""
        self.test.reports_collection.generate_report()
