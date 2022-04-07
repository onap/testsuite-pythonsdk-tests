"""Instantiate basic vm using SO macro flow."""
import logging
import time

from onapsdk.configuration import settings
from onapsdk.exceptions import SDKException
from xtesting.core import testcase

from onaptests.utils.exceptions import OnapTestException
from onaptests.steps.instantiate.service_macro import YamlTemplateServiceMacroInstantiateStep


class BasicVmMacroStability(testcase.TestCase):
    """Instantiate a basic vm macro."""

    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        """Init Basic Macro use case."""
        if "case_name" not in kwargs:
            kwargs["case_name"] = 'basic_vm_macro_stability'
        super().__init__(**kwargs)
        self.__logger.debug("Basic VM macro stability init started")
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
