#!/usr/bin/env python
"""vIMS VM test case."""
import logging
import time

from onapsdk.configuration import settings
from onapsdk.exceptions import SDKException
from onaptests.scenario.scenario_base import ScenarioBase
from onaptests.steps.instantiate.vf_module_ala_carte import \
    YamlTemplateVfModuleAlaCarteInstantiateStep
from onaptests.utils.exceptions import OnapTestException


class ClearwaterIms(ScenarioBase):
    """Onboard then instantiate a clearwater vIMS with ONAP."""

    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        """Init Clearwater IMS."""
        # import clearwater_ims_nomulticloud_settings needed
        super().__init__('clearwater_ims', **kwargs)
        self.test = YamlTemplateVfModuleAlaCarteInstantiateStep()
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
        except OnapTestException as exc:
            self.result = 0
            self.__logger.error(exc.error_message)
        except SDKException:
            self.result = 0
            self.__logger.error("SDK Exception")
        finally:
            self.stop_time = time.time()

    def clean(self):
        """Clean Additional resources if needed."""
        try:
            self.test.reports_collection.generate_report()
        except:  # noqa
            self.__logger.error("Impossible to generate reporting")
