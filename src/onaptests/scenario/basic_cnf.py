#!/usr/bin/env python
"""Basic CNF test case."""
import logging
import time

from xtesting.core import testcase
from onaptests.configuration import settings

import onaptests.utils.exceptions as onap_test_exceptions
from onaptests.steps.instantiate.vf_module_ala_carte import YamlTemplateVfModuleAlaCarteInstantiateStep

class BasicCnf(testcase.TestCase):
    """Onboard then instantiate a simple CNF with ONAP."""

    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        """Init BasicCnf."""
        if "case_name" not in kwargs:
            kwargs["case_name"] = 'basic_cnf'
        super(BasicCnf, self).__init__(**kwargs)
        self.__logger.debug("BasicCnf init started")
        self.test = YamlTemplateVfModuleAlaCarteInstantiateStep(
                cleanup=settings.CLEANUP_FLAG)
        self.start_time = None
        self.stop_time = None
        self.result = 0

    def run(self):
        """Run onap_tests with basic_cnf VM."""
        self.start_time = time.time()
        self.__logger.debug("start time")
        try:
            self.test.execute()
            self.__logger.info("basic_cnf successfully created")
            # The cleanup is part of the test, not only a teardown action
            if settings.CLEANUP_FLAG:
                self.__logger.info("basic_cnf cleanup called")
                time.sleep(settings.CLEANUP_ACTIVITY_TIMER)
                self.test.cleanup()
                self.result = 100
            else:
                self.__logger.info("No cleanup requested. Test completed.")
                self.result = 100
        except onap_test_exceptions.OnapTestException as exc:
            self.result = 0
            self.__logger.error(exc.error_message)
        finally:
            self.stop_time = time.time()

    def clean(self):
        """Clean Additional resources if needed."""
        self.__logger.info("Generate Test report")
        self.test.reports_collection.generate_report()
