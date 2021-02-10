#!/usr/bin/env python
"""Basic VM test case."""
import logging
import time

from xtesting.core import testcase
from onapsdk.configuration import settings
from onapsdk.exceptions import SDKException

from onaptests.steps.instantiate.vf_module_ala_carte import YamlTemplateVfModuleAlaCarteInstantiateStep
from onaptests.utils.exceptions import OnapTestException

class BasicVm(testcase.TestCase):
    """Onboard then instantiate a simple VM with ONAP."""

    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        """Init BasicVM."""
        if "case_name" not in kwargs:
            kwargs["case_name"] = 'basic_vm'
        super(BasicVm, self).__init__(**kwargs)
        self.__logger.debug("BasicVm init started")
        self.test = YamlTemplateVfModuleAlaCarteInstantiateStep(
                cleanup=settings.CLEANUP_FLAG)
        self.start_time = None
        self.stop_time = None
        self.result = 0

    def run(self):
        """Run Basic VM onap test."""
        self.start_time = time.time()
        self.__logger.debug("start time")
        try:
            self.test.execute()
            self.__logger.info("VNF basic_vm successfully created")
            # The cleanup is part of the test, not only a teardown action
            if settings.CLEANUP_FLAG:
                self.__logger.info("VNF basic_vm cleanup called")
                time.sleep(settings.CLEANUP_ACTIVITY_TIMER)
                self.test.cleanup()
                self.result = 100
            else:
                self.__logger.info("No cleanup requested. Test completed.")
                self.result = 100
        except (OnapTestException, SDKException) as exc:
            self.result = 0
            self.__logger.error(exc.error_message)
        finally:
            self.stop_time = time.time()

    def clean(self):
        """Clean Additional resources if needed."""
        self.__logger.info("Generate Test report")
        self.test.reports_collection.generate_report()
