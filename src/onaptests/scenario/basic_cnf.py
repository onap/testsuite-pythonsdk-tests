#!/usr/bin/env python
"""Basic CNF test case."""
import logging
import time

from xtesting.core import testcase
from onapsdk.configuration import settings
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
        except onap_test_exceptions.TestConfigurationException:
            self.result = 0
            self.__logger.error("Basic CNF configuration error")
        except onap_test_exceptions.ServiceInstantiateException:
            self.result = 0
            self.__logger.error("Basic CNF service instantiation error")
        except onap_test_exceptions.ServiceCleanupException:
            self.result = 0
            self.__logger.error("Basic CNF service instance cleanup error")
        except onap_test_exceptions.VnfInstantiateException:
            self.result = 0
            self.__logger.error("Basic CNF Vnf instantiation error")
        except onap_test_exceptions.VnfCleanupException:
            self.result = 0
            self.__logger.error("Basic CNF Vnf instance cleanup error")
       except onap_test_exceptions.ProfileInformationException:
            self.__logger.error("Missing k8s profile information")
            self.result = 0
       except onap_test_exceptions.ProfileCleanupException:
            self.__logger.error("K8s profile deletion failed")
            self.result = 0
        except onap_test_exceptions.VfModuleInstantiateException:
            self.result = 0
            self.__logger.error("Basic CNF Module instantiation error")
        except onap_test_exceptions.VfModuleCleanupException:
            self.__logger.error("Basic CNF Module cleanup failed.")
            self.result = 0
        finally:
            self.stop_time = time.time()

    def clean(self):
        """Clean Additional resources if needed."""
        self.__logger.info("Generate Test report")
        self.test.reports_collection.generate_report()
