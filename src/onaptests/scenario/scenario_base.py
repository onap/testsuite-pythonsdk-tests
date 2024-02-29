import logging
import time

from onapsdk.configuration import settings
from onapsdk.exceptions import SDKException, SettingsError
from xtesting.core import testcase

from onaptests.steps.base import BaseStep, YamlTemplateBaseStep
from onaptests.utils.exceptions import (OnapTestException,
                                        TestConfigurationException)


class ScenarioBase(testcase.TestCase):
    """Scenario base class."""

    __logger = logging.getLogger()

    def __init__(self, case_name_override, **kwargs):
        """Init base scenario."""
        if "case_name" not in kwargs:
            kwargs["case_name"] = case_name_override
        self.case_name = kwargs["case_name"]
        self.scenario_name = self.case_name.replace("_", " ")
        self.scenario_name = str.title(self.scenario_name)

        self.__logger.info("%s Global Configuration:", self.scenario_name)
        for val_name, val in settings._settings.items():
            self.__logger.info("%s: %s", val_name, val)

        self.__logger.debug("%s init started", self.scenario_name)
        super().__init__(**kwargs)
        self.general_exception = None
        self.test: BaseStep = None

    def run(self, **kwargs):
        """Run scenario and cleanup resources afterwards"""
        self.start_time = time.time()
        try:
            for test_phase in (self.test.execute, self.test.cleanup):
                phase_name = test_phase.__name__
                try:
                    if (phase_name == "cleanup" and settings.CLEANUP_FLAG and
                            settings.CLEANUP_ACTIVITY_TIMER > 0):
                        time.sleep(settings.CLEANUP_ACTIVITY_TIMER)
                    self.__logger.info("%s %s Phase Started",
                                       self.scenario_name, phase_name.title())
                    test_phase()
                    self.result += 50
                except OnapTestException as exc:
                    self.__logger.exception("Test Exception %s on %s", str(exc), phase_name)
                    self.__logger.info("ROOT CAUSE")
                    self.__logger.info(exc.root_cause)
                except SDKException as exc:
                    self.__logger.exception("SDK Exception %s on %s", str(exc), phase_name)
                    self.__logger.info("ROOT CAUSE")
                    self.__logger.info(str(exc))
                except Exception as exc:
                    self.__logger.exception("General Exception %s on %s", str(exc), phase_name)
                    if self.general_exception:
                        exc = ExceptionGroup("General Exceptions", [self.general_exception, exc])  # noqa
                    self.general_exception = exc
        finally:
            self.stop_time = time.time()
            self.__logger.info(f"{self.scenario_name} Execution {self.result}% Completed")
        if self.general_exception:
            raise self.general_exception

    def clean(self):
        """Clean Additional resources if needed."""
        self.__logger.info("Generate %s Test report", self.scenario_name)
        self.test.reports_collection.generate_report()

    def validate(self):
        """Validate implementation of the scenario."""

        self._validate_service_details()
        self.test.validate_step_implementation()
        self.test.validate_execution()
        self.test.validate_cleanup()

    def _validate_service_details(self):
        self._check_setting("SERVICE_NAME")
        self._check_setting("SERVICE_DETAILS")

    def _check_setting(self, name: str):
        try:
            if getattr(settings, name) == "":
                raise TestConfigurationException(
                    f"[{self.case_name}] {name} setting is not defined")
        except (KeyError, AttributeError, SettingsError) as exc:
            raise TestConfigurationException(
                f"[{self.case_name}] {name} setting is not defined") from exc


class BaseScenarioStep(BaseStep):
    """Main scenario step that has no own execution method."""

    def __init__(self, cleanup=False):
        """Initialize BaseScenarioStep step."""
        super().__init__(cleanup=cleanup)

    @BaseStep.store_state
    def execute(self) -> None:
        super().execute()


class YamlTemplateBaseScenarioStep(YamlTemplateBaseStep, BaseScenarioStep):
    """Main scenario yaml template step that has no own execution method."""

    def __init__(self, cleanup=False):
        """Initialize YamlTemplateBaseScenarioStep step."""
        super().__init__(cleanup=cleanup)
