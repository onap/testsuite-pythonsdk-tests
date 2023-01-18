#!/usr/bin/env python
"""Basic CPS test case."""
import logging
import time
from xtesting.core import testcase
from onapsdk.configuration import settings
from onapsdk.exceptions import SDKException
from onaptests.steps.onboard.service import YamlTemplateServiceOnboardStep
from onaptests.utils.exceptions import OnapTestException

class BasicCps(testcase.TestCase):
    """Create CPS resources:
            - dataspace
            - schemaset
            - anchor
        And create a node. Use bookstore YANG model (available on CPS repository
        https://github.com/onap/cps/blob/master/cps-service/src/test/resources/bookstore.yang).
        At the end delete what's available to be deleted.

    """

    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        """Init Basic CPS."""
        if "case_name" not in kwargs:
            kwargs["case_name"] = 'basic_cps'
        super().__init__(**kwargs)
        self.__logger.debug("BasicCps init started")
        # self.test = YamlTemplateServiceOnboardStep(  # To be created
        #     cleanup=settings.CLEANUP_FLAG)
        self.start_time = None
        self.stop_time = None
        self.result = 0

    def run(self):
        """Run basic_cps and create some CPS resources"""
        self.start_time = time.time()
        self.__logger.debug("start time")
        try:
            self.test.execute()
            self.test.cleanup()
            self.__logger.info("Basic CPS test passed")
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
