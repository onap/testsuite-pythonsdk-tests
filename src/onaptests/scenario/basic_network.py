#!/usr/bin/env python
"""Basic VM test case."""
import logging
import time

from xtesting.core import testcase
from onapsdk.configuration import settings

import onaptests.utils.exceptions as onap_test_exceptions
from onaptests.steps.instantiate.vl_ala_carte import YamlTemplateVlAlaCarteInstantiateStep

class BasicNetwork(testcase.TestCase):
    """Onboard then instantiate a simple Network with ONAP."""

    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        """Init Basic Network use case."""
        # import basic_network_nomulticloud_settings needed
        if "case_name" not in kwargs:
            kwargs["case_name"] = 'basic_network'
        super(BasicNetwork, self).__init__(**kwargs)
        self.__logger.debug("BasicNetwork init started")
        self.test = YamlTemplateVlAlaCarteInstantiateStep(
                cleanup=settings.CLEANUP_FLAG)
        self.start_time = None
        self.stop_time = None
        self.result = 0

    def run(self):
        """Run onap_tests with basic network."""
        self.start_time = time.time()
        self.__logger.debug("start time")
        try:
            self.test.execute()
            self.__logger.info("Service basic_network successfully created")
            # The cleanup is part of the test, not only a teardown action
            if settings.CLEANUP_FLAG:
                self.__logger.info("Service basic_network cleanup called")
                time.sleep(settings.CLEANUP_ACTIVITY_TIMER)
                try:
                    self.test.cleanup()
                except ValueError as error:
                    self.__logger.info("service deleted as expected {0}".format(error))
                self.result = 100
            else:
                self.__logger.info("No cleanup requested. Test completed.")
                self.result = 100
        except onap_test_exceptions.ServiceInstantiateException:
            self.__logger.error("Basic network service instantiation failed.")
            self.result = 0
        except onap_test_exceptions.ServiceInstantiateException:
            self.__logger.error("Basic network service cleanup failed.")
            self.result = 0
        except onap_test_exceptions.NetworkInstantiateException:
            self.__logger.error("Basic network VL instantiation failed.")
            self.result = 0
        except onap_test_exceptions.NetworkCleanupException:
            self.__logger.error("Basic network VL cleanup failed.")
            self.result = 0
        finally:
            self.stop_time = time.time()

    def clean(self):
        """Clean Additional resources if needed."""
        self.__logger.info("Generate Test report")
        self.test.reports_collection.generate_report()
