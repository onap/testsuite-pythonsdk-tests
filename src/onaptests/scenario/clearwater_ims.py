#!/usr/bin/env python
"""vIMS VM test case."""
import logging
import time

from xtesting.core import testcase
from onapsdk.configuration import settings
from onaptests.steps.instantiate.vf_module_ala_carte import YamlTemplateVfModuleAlaCarteInstantiateStep

class ClearwaterIms(testcase.TestCase):
    """Onboard then instantiate a clearwater vIMS with ONAP."""

    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        """Init Clearwater IMS."""
        # import clearwater_ims_nomulticloud_settings needed
        if "case_name" not in kwargs:
            kwargs["case_name"] = 'clearwater_ims'
        super(ClearwaterIms, self).__init__(**kwargs)
        self.__logger.debug("vIMS init started")
        self.test = YamlTemplateVfModuleAlaCarteInstantiateStep(
                cleanup=settings.CLEANUP_FLAG)
        self.start_time = None
        self.stop_time = None
        self.result = 0

    def run(self):
        """Run vIMS test."""
        self.start_time = time.time()
        self.__logger.debug("start time")
        try:
            self.test.execute()
            self.__logger.info("VNF clearwater IMS successfully created")
            # The cleanup is part of the test, not only a teardown action
            if settings.CLEANUP_FLAG:
                self.__logger.info("VNF clearwater IMS cleanup called")
                time.sleep(settings.CLEANUP_ACTIVITY_TIMER)
                self.test.cleanup()
                self.result = 100
            else:
                self.__logger.info("No cleanup requested. Test completed.")
                self.result = 100
            self.stop_time = time.time()
        except:
            self.__logger.error("Clearwater IMS test case failed.")
            self.result = 0
            self.stop_time = time.time()

    def clean(self):
        """Clean Additional resources if needed."""
        try:
            self.test.reports_collection.generate_report()
        except:
            self.__logger.error("Impossible to generate reporting")
