#!/usr/bin/env python
"""Basic VM test case."""
import logging
import os
import time

from xtesting.core import testcase
from onapsdk.configuration import settings
from onaptests.steps.instantiate.vf_module_ala_carte import YamlTemplateVfModuleAlaCarteInstantiateStep

class BasicVm(testcase.TestCase):
    """Onboard then instantiate a simple VM though ONAP."""

    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        """Init BasicVM."""
        if "case_name" not in kwargs:
            kwargs["case_name"] = 'basic_vm'
        super(BasicVm, self).__init__(**kwargs)
        os.environ["ONAP_PYTHON_SDK_SETTINGS"] = "onaptests.configuration.ubuntu16_nomulticloudsettings"
        self.__logger.debug("BasicVm init started")
        self.test = YamlTemplateVfModuleAlaCarteInstantiateStep(
                cleanup=settings.CLEANUP_FLAG)
        self.start_time = None
        self.stop_time = None
        self.result = 0

    def run(self):
        """Run onap_tests with ubuntu16 VM."""
        self.start_time = time.time()
        self.__logger.debug("start time")
        self.test.execute()
        self.__logger.info("VNF basic_vm successfully created")
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
