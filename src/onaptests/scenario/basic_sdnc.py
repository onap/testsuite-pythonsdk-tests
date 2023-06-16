import logging
import time

from onapsdk.configuration import settings
from onapsdk.exceptions import SDKException
from onaptests.scenario.scenario_base import ScenarioBase
from onaptests.steps.instantiate.sdnc_service import TestSdncStep
from onaptests.utils.exceptions import OnapTestException
from xtesting.core import testcase


class BasicSdnc(ScenarioBase):
    """Create SDNC service.
    Check and delete the service.
    """

    __logger = logging.getLogger()

    def __init__(self, **kwargs):
        """Init Basic SDNC use case."""
        super().__init__('basic_sdnc', **kwargs)
        self.test = TestSdncStep(cleanup=settings.CLEANUP_FLAG)

    def run(self):
        """Run basic SDNC test."""
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
