import logging
import time

from onapsdk.configuration import settings
from onapsdk.exceptions import SDKException
from onaptests.utils.exceptions import OnapTestException
from xtesting.core import testcase


class ScenarioBase(testcase.TestCase):
    """Scenario base class."""

    __logger = logging.getLogger()

    def __init__(self, case_name_override, **kwargs):
        """Init base scenario."""
        if "case_name" not in kwargs:
            kwargs["case_name"] = case_name_override
        self.scenario_name = kwargs["case_name"].replace("_", " ")
        self.scenario_name = str.title(self.scenario_name)

        self.__logger.info("%s Global Configuration:", self.scenario_name)
        for val in settings._settings:
            self.__logger.info("%s: %s", val, settings._settings[val])

        self.__logger.debug("%s init started", self.scenario_name)
        super().__init__(**kwargs)
        self.general_exception = None

    def run(self):
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
                    self.__logger.exception("%s on %s", exc.error_message, phase_name)
                except SDKException:
                    self.__logger.exception("SDK Exception on %s", phase_name)
                except Exception as e:
                    self.__logger.exception("General Exception on %s", phase_name)
                    self.general_exception = e
        finally:
            self.stop_time = time.time()
            self.__logger.info("%s Execution Completed after %s",
                               self.scenario_name, self.get_duration())
        if self.general_exception:
            raise self.general_exception

    def clean(self):
        """Clean Additional resources if needed."""
        self.__logger.info("Generate %s Test report", self.scenario_name)
        self.test.reports_collection.generate_report()
