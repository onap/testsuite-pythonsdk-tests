#!/usr/bin/env python
"""Simple CDS blueprint erichment test scenario."""

import logging
import time

from onapsdk.configuration import settings
from xtesting.core import testcase

import onaptests.utils.exceptions as onap_test_exceptions
from onaptests.steps.onboard.cds import CbaEnrichStep


class CDSBlueprintEnrichment(testcase.TestCase):
    """Enrich simple blueprint using CDS blueprintprocessor."""

    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        """Init CDS blueprint enrichment use case."""
        if "case_name" not in kwargs:
            kwargs["case_name"] = 'basic_cds'
        super(CDSBlueprintEnrichment, self).__init__(**kwargs)
        self.__logger.debug("CDS blueprint enrichment initialization")
        self.test = CbaEnrichStep(
                cleanup=settings.CLEANUP_FLAG)
        self.start_time = None
        self.stop_time = None
        self.result = 0

    def run(self):
        self.__logger.debug("CDS blueprint enrichment run")
        self.start_time = time.time()
        self.test.execute()
        self.result = 100
        self.stop_time = time.time()

    def clean(self):
        """Clean Additional resources if needed."""
        self.__logger.info("Generate Test report")
        self.test.reports_collection.generate_report()
