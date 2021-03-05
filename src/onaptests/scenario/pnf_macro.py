"""Instantiate service with PNF using SO macro flow."""
import logging
import time
from yaml import load

from xtesting.core import testcase
from onapsdk.configuration import settings
from onapsdk.exceptions import SDKException

from onaptests.steps.base import YamlTemplateBaseStep
from onaptests.steps.onboard.cds import CbaEnrichStep
from onaptests.steps.simulator.pnf_simulator_cnf.pnf_register import PnfSimulatorCnfRegisterStep
from onaptests.steps.instantiate.service_macro import YamlTemplateServiceMacroInstantiateStep
from onaptests.utils.exceptions import OnapTestException


class PnfMacroScenarioStep(YamlTemplateBaseStep):
    """Step created to run scenarion and generate report."""

    def __init__(self, cleanup=False):
        """Initialize step.

        Substeps:
            - YamlTemplateServiceAlaCarteInstantiateStep.
        """
        super().__init__(cleanup=cleanup)
        self._yaml_template: dict = None
        self.add_step(PnfSimulatorCnfRegisterStep(
            cleanup=settings.CLEANUP_FLAG
        ))
        self.add_step(CbaEnrichStep(
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
                self._yaml_template: dict = load(yaml_template)
        return self._yaml_template

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


class PnfMacro(testcase.TestCase):
    """Run PNF simulator and onboard then instantiate a service with PNF."""

    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        """Init Basic Network use case."""
        if "case_name" not in kwargs:
            kwargs["case_name"] = 'pnf_macro'
        super().__init__(**kwargs)
        self.__logger.debug("PnfMacro init started")
        self.test = PnfMacroScenarioStep(cleanup=settings.CLEANUP_FLAG)

    def run(self):
        """Run PNF macro test."""
        self.start_time = time.time()
        try:
            self.test.execute()
            self.test.cleanup()
            self.result = 100
        except (OnapTestException, SDKException) as exc:
            self.result = 0
            self.__logger.error(exc.error_message)
        finally:
            self.stop_time = time.time()

    def clean(self):
        """Generate report."""
        self.test.reports_collection.generate_report()
