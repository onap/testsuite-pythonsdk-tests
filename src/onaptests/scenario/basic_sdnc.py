import logging
import time
from xtesting.core import testcase

from onapsdk.configuration import settings
from onapsdk.exceptions import SDKException

from onaptests.steps.instantiate.sdnc_service import UpdateSdncService
from onaptests.utils.exceptions import OnapTestException


class BasicSdnc(testcase.TestCase):
    """Create SDNC service.
    Check and delete the service.
    """

    __logger = logging.getLogger()

    def __init__(self, **kwargs):
        """Init Basic SDNC use case."""
        if "case_name" not in kwargs:
            kwargs["case_name"] = 'basic_SDNC'
        super().__init__(**kwargs)
        self.__logger.debug("Basic SDNC init started")
        self.test = UpdateSdncService(cleanup=settings.CLEANUP_FLAG)

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
