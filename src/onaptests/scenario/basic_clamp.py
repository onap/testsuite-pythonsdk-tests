"""Basic Clamp test case."""
import logging
import time

from onapsdk.configuration import settings
from onapsdk.exceptions import APIError, SDKException
from onaptests.scenario.scenario_base import ScenarioBase
from onaptests.steps.loop.clamp import ClampStep
from onaptests.utils.exceptions import OnapTestException
from xtesting.core import testcase


class BasicClamp(ScenarioBase):
    """Onboard, update a model with a loop, design the loop and deploy it."""
    __logger = logging.getLogger(__name__)
    def __init__(self, **kwargs):
        """Init Basic Clamp, onboard a VM, design and deploy a loop with CLAMP."""
        super().__init__('basic_clamp', **kwargs)
        self.test = ClampStep(
                cleanup=settings.CLEANUP_FLAG)
        self.start_time = None
        self.stop_time = None
        self.result = 0

    def run(self):
        """Run Basic CLAMP onap test."""
        self.start_time = time.time()
        self.__logger.debug("start time")
        try:
            self.test.execute()
            self.__logger.info("VNF basic_clamp successfully created")
            # The cleanup is part of the test, not only a teardown action
            if settings.CLEANUP_FLAG:
                self.__logger.info("VNF basic_clamp cleanup called")
                time.sleep(settings.CLEANUP_ACTIVITY_TIMER)
                self.test.cleanup()
                self.result = 100
            else:
                self.__logger.info("No cleanup requested. Test completed.")
                self.result = 100
        except OnapTestException as exc:
            self.result = 0
            self.__logger.exception(exc.error_message)
        except (SDKException, APIError):
            self.result = 0
            self.__logger.exception("SDK exception")
        finally:
            self.stop_time = time.time()

    def clean(self):
        """Clean Additional resources if needed."""
        self.__logger.info("Generate Test report")
        self.test.reports_collection.generate_report()
