#!/usr/bin/env python
"""Basic Onboard test case."""
import logging
import time
from xtesting.core import testcase
from onapsdk.configuration import settings
from onapsdk.exceptions import SDKException
from onaptests.steps.onboard.service import YamlTemplateServiceOnboardStep
from onaptests.utils.exceptions import OnapTestException

class BasicOnboard(testcase.TestCase):
    """Onboard a simple VM with ONAP."""

    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        """Init BasicOnboard."""
        # import basic_onboard_settings needed
        if "case_name" not in kwargs:
            kwargs["case_name"] = 'basic_onboard'
        super(BasicOnboard, self).__init__(**kwargs)
        self.__logger.debug("BasicOnboard init started")
        self.test = YamlTemplateServiceOnboardStep(
            cleanup=settings.CLEANUP_FLAG)
        self.start_time = None
        self.stop_time = None
        self.result = 0

    def run(self):
        """Run basic_onboard and onboard a simple service"""
        self.start_time = time.time()
        self.__logger.debug("start time")
        try:
            self.test.execute()
            self.__logger.info("VNF basic_vm successfully onboarded")
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
