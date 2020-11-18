#!/usr/bin/env python
"""Simple CDS blueprint erichment test scenario."""

import logging

from onapsdk.configuration import settings
from xtesting.core import testcase

from onaptests.steps.onboard.cds import CbaEnrichStep


class CDSBlueprintEnrichment(testcase.TestCase):
    """Enrich simple blueprint using CDS blueprintprocessor."""

    __logger = logging.getLogger(__name__)

    def __init__(self):
        """Init CDS blueprint enrichment use case."""
        self.__logger.debug("CDS blueprint enrichment initialization")
        super.__init__()
        self.test = CbaEnrichStep(
                cleanup=settings.CLEANUP_FLAG)

    def run(self):
        self.__logger.debug("CDS blueprint enrichment run")
        self.test.execute()

    def clean(self):
        """Clean Additional resources if needed."""
        self.__logger.info("Generate Test report")
        self.test.reports_collection.generate_report()


if __name__ == "__main__":
    c = CDSBlueprintEnrichment()
    c.run()
    c.clean()
