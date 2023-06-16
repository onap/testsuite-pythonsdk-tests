import logging
import time

from onapsdk.configuration import settings
from onapsdk.exceptions import SDKException
from onaptests.scenario.scenario_base import ScenarioBase
from onaptests.steps.cloud.check_status import CheckNamespaceStatusStep
from onaptests.utils.exceptions import OnapTestException
from xtesting.core import testcase


class Status(ScenarioBase):
    """Retrieve status of Kubernetes resources in the nemaspace."""

    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        """Init the testcase."""
        super().__init__('status', **kwargs)
        self.test = CheckNamespaceStatusStep(
                cleanup=settings.CLEANUP_FLAG)
        self.start_time = None
        self.stop_time = None
        self.result = 0

    def run(self):
        """Status check test."""
        self.start_time = time.time()
        self.__logger.debug("start time")
        try:
            self.test.execute()
            self.__logger.info("Status check successfully completed")
            # The cleanup is part of the test, not only a teardown action
            if settings.CLEANUP_FLAG:
                self.__logger.info("Status check cleanup called")
                time.sleep(settings.CLEANUP_ACTIVITY_TIMER)
                self.test.cleanup()
                self.result = 100
            else:
                self.__logger.info("No cleanup requested. Test completed.")
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
        """Clean Additional resources if needed."""
        self.__logger.info("Generate Test report")
        self.test.reports_collection.generate_report()
