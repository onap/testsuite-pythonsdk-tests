"""Instantiate basic cnf using SO macro flow."""
import logging
import time

from onapsdk.configuration import settings
from onapsdk.exceptions import SDKException
from onaptests.scenario.scenario_base import ScenarioBase
from onaptests.steps.base import YamlTemplateBaseStep
from onaptests.steps.instantiate.service_macro import \
    YamlTemplateServiceMacroInstantiateStep
from onaptests.steps.onboard.cds import CbaPublishStep
from onaptests.utils.exceptions import OnapTestException
from xtesting.core import testcase
from yaml import SafeLoader, load


class BasicCnfMacroStep(YamlTemplateBaseStep):

    def __init__(self, cleanup=False):
        """Initialize step.

        Substeps:
            - CbaPublishStep
            - YamlTemplateServiceMacroInstantiateStep.
        """
        super().__init__(cleanup=cleanup)
        self._yaml_template: dict = None
        self.add_step(CbaPublishStep(
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
        return "Basic CNF macro scenario step"

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


class BasicCnfMacro(ScenarioBase):
    """Instantiate a basic cnf macro."""

    __logger = logging.getLogger()

    def __init__(self, **kwargs):
        """Init Basic Cnf Macro use case."""
        super().__init__('basic_cnf_macro', **kwargs)
        self.test = BasicCnfMacroStep(cleanup=settings.CLEANUP_FLAG)

    def run(self):
        """Run basic cnf macro test."""
        self.start_time = time.time()
        try:
            self.test.execute()
            self.test.cleanup()
            self.result = 100
        except OnapTestException as exc:
            self.result = 0
            self.__logger.exception(exc.error_message)
        except SDKException:
            self.result = 0
            self.__logger.exception("SDK Exception")
        finally:
            self.stop_time = time.time()

    def clean(self):
        """Generate report."""
        self.test.reports_collection.generate_report()
