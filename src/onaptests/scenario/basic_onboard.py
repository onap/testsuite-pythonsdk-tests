#!/usr/bin/env python
"""Basic Onboard test case."""
import logging
import time

from onapsdk.configuration import settings
from onapsdk.exceptions import SDKException
from onaptests.scenario.scenario_base import ScenarioBase
from onaptests.steps.onboard.service import YamlTemplateServiceOnboardStep
from onaptests.utils.exceptions import OnapTestException
from xtesting.core import testcase


class BasicOnboard(ScenarioBase):
    """Onboard a simple VM with ONAP."""

    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        """Init BasicOnboard."""
        # import basic_onboard_settings needed
        super().__init__('basic_onboard', **kwargs)
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
            self.test.cleanup()
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
