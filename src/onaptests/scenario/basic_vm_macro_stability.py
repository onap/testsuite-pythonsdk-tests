"""Instantiate basic vm using SO macro flow."""
import logging
import time

from onapsdk.configuration import settings
from onapsdk.exceptions import SDKException
from onaptests.scenario.scenario_base import ScenarioBase
from onaptests.steps.instantiate.service_macro import \
    YamlTemplateServiceMacroInstantiateStep
from onaptests.utils.exceptions import OnapTestException
from xtesting.core import testcase


class BasicVmMacroStability(ScenarioBase):
    """Instantiate a basic vm macro."""

    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        """Init Basic Macro use case."""
        super().__init__('basic_vm_macro_stability', **kwargs)
        self.test = YamlTemplateServiceMacroInstantiateStep(cleanup=settings.CLEANUP_FLAG)

    def run(self):
        """Run basic vm macro test."""
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
