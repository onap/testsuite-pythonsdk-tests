#!/usr/bin/env python
"""Basic VM test case."""
import logging
import time

from onapsdk.configuration import settings
from onapsdk.exceptions import SDKException
from onaptests.scenario.scenario_base import ScenarioBase
from onaptests.steps.instantiate.vf_module_ala_carte import \
    YamlTemplateVfModuleAlaCarteInstantiateStep
from onaptests.utils.exceptions import OnapTestException
from xtesting.core import testcase


class BasicVm(ScenarioBase):
    """Onboard then instantiate a simple VM with ONAP."""

    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        """Init BasicVM."""
        super().__init__('basic_vm', **kwargs)
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
