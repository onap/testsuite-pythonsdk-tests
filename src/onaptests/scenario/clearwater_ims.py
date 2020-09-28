#!/usr/bin/env python
"""vIMS VM test case."""
import logging
import time

from xtesting.core import testcase
from onapsdk.configuration import settings
from onaptests.steps.instantiate.vf_module_ala_carte import YamlTemplateVfModuleAlaCarteInstantiateStep

class ClearwaterIms(testcase.TestCase):
    """Onboard then instantiate a simple VM though ONAP."""

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
        self.test.execute()
        self.__logger.info("vIMS successfully created")
        # Space for running additional tests on the deployed VNF here
        if not settings.CLEANUP_FLAG:
            self.result = 100
            self.stop_time = time.time()
            return testcase.TestCase.EX_OK

    def clean(self):
        """Clean VNF."""
        if settings.CLEANUP_FLAG:
            time.sleep(settings.CLEANUP_ACTIVITY_TIMER)
        try:
            self.test.cleanup()
        except ValueError as error:
            self.__logger.info("service instance deleted as expected {0}".format(error))
            self.result = 100
            self.stop_time = time.time()
            return testcase.TestCase.EX_OK
