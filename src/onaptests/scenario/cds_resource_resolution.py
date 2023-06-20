#!/usr/bin/env python
"""CDS resource resolution test scenario."""

import logging
import time

from onapsdk.configuration import settings
from onapsdk.exceptions import SDKException
from onaptests.scenario.scenario_base import ScenarioBase
from onaptests.steps.base import BaseStep
from onaptests.steps.onboard.cds import CbaProcessStep
from onaptests.steps.simulator.cds_mockserver import \
    CdsMockserverCnfConfigureStep
from onaptests.utils.exceptions import OnapTestException


class CDSResourceResolutionStep(BaseStep):
    """Step created to run scenario and generate report."""

    def __init__(self, cleanup=False):
        """Initialize step.

        Substeps:
            - CdsMockserverCnfConfigureStep,
            - CbaProcessStep.
        """
        super().__init__(cleanup=cleanup)
        self.add_step(CdsMockserverCnfConfigureStep(
            cleanup=cleanup
        ))
        self.add_step(CbaProcessStep(
            cleanup=cleanup
        ))

    @property
    def description(self) -> str:
        """Step description.

        Used for reports

        Returns:
            str: Step description

        """
        return "CDS resource-resoulution base step"

    @property
    def component(self) -> str:
        """Component name.

       Name of the component this step relates to.
            Usually the name of ONAP component.

        Returns:
            str: Component name

        """
        return "PythonSDK-tests"


class CDSResourceResolution(ScenarioBase):
    """Enrich simple blueprint using CDS blueprintprocessor."""

    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        """Init CDS resource resolution use case."""
        super().__init__('basic_cds', **kwargs)
        self.test = CDSResourceResolutionStep(
                cleanup=settings.CLEANUP_FLAG)
        self.start_time = None
        self.stop_time = None
        self.result = 0

    def run(self):
        self.__logger.debug("CDS resource resolution run")
        self.start_time = time.time()
        try:
            for test_phase in (self.test.execute, self.test.cleanup):
                try:
                    test_phase()
                    self.result += 50
                except OnapTestException as exc:
                    self.__logger.exception(exc.error_message)
                except SDKException:
                    self.__logger.exception("SDK Exception")
        finally:
            self.stop_time = time.time()

    def clean(self):
        """Clean Additional resources if needed."""
        self.__logger.info("Generate Test report")
        self.test.reports_collection.generate_report()
