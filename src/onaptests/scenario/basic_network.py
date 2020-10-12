#!/usr/bin/env python
"""Basic VM test case."""
import logging
import time

from xtesting.core import testcase
from onapsdk.configuration import settings
from onaptests.steps.instantiate.vl_ala_carte import YamlTemplateVlAlaCarteInstantiateStep

class BasicNw(testcase.TestCase):
    """Onboard then instantiate a simple Network with ONAP."""

    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        """Init BasicNw."""
        # import basic_network_nomulticloud_settings needed
        if "case_name" not in kwargs:
            kwargs["case_name"] = 'basic_network'
        super(BasiciNw, self).__init__(**kwargs)
        self.__logger.debug("BasicNw init started")
        self.test = YamlTemplateVlAlaCarteInstantiateStep(
                cleanup=settings.CLEANUP_FLAG)
        self.start_time = None
        self.stop_time = None
        self.result = 0

    def run(self):
        """Run onap_tests with basic network."""
        self.start_time = time.time()
        self.__logger.debug("start time")
        self.test.execute()
        self.__logger.info("Service basic_network successfully created")
        self.stop_time = time.time()
        # The cleanup is part of the test, not only a teardown action
        if settings.CLEANUP_FLAG:
            self.__logger.info("Service basic_network cleanup called")
            time.sleep(settings.CLEANUP_ACTIVITY_TIMER)
            self.test.cleanup()
            self.result = 100
        else:
            self.__logger.info("No cleanup requested. Test completed.")
            self.result = 100

    def clean(self):
        """Clean Additional resources if needed."""
        self.__logger.info("Generate Test report")
        self.test.reports_collection.generate_report()
