#!/usr/bin/env python
"""Simple CDS blueprint erichment test scenario."""

import logging
import time

from onapsdk.configuration import settings
from onapsdk.exceptions import SDKException
from onaptests.scenario.scenario_base import ScenarioBase
from onaptests.steps.onboard.cds import CbaEnrichStep
from onaptests.utils.exceptions import OnapTestException
from xtesting.core import testcase


class CDSBlueprintEnrichment(ScenarioBase):
    """Enrich simple blueprint using CDS blueprintprocessor."""

    __logger = logging.getLogger()

    def __init__(self, **kwargs):
        """Init CDS blueprint enrichment use case."""
        super().__init__('basic_cds', **kwargs)
        self.test = CbaEnrichStep(
                cleanup=settings.CLEANUP_FLAG)
        self.start_time = None
        self.stop_time = None
        self.result = 0

    def run(self):
        self.__logger.debug("CDS blueprint enrichment run")
        self.start_time = time.time()
        try:
            self.test.execute()
            if settings.CLEANUP_FLAG:
                self.test.cleanup()
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
