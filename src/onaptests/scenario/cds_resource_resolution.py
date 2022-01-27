#!/usr/bin/env python
"""CDS resource resolution test scenario."""

import logging
import time

from onapsdk.configuration import settings
from onapsdk.exceptions import SDKException
from xtesting.core import testcase

from onaptests.steps.base import BaseStep
from onaptests.steps.onboard.cds import CbaProcessStep
from onaptests.steps.simulator.cds_mockserver import CdsMockserverCnfConfigureStep
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


class CDSResourceResolution(testcase.TestCase):
    """Enrich simple blueprint using CDS blueprintprocessor."""

    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        """Init CDS resource resolution use case."""
        if "case_name" not in kwargs:
            kwargs["case_name"] = 'basic_cds'
        super().__init__(**kwargs)
        self.__logger.debug("CDS resource resolution initialization")
        self.test = CDSResourceResolutionStep(
                cleanup=settings.CLEANUP_FLAG)
        self.start_time = None
        self.stop_time = None
        self.result = 0

    def run(self):
        self.__logger.debug("CDS resource resolution run")
        self.start_time = time.time()
        try:
            self.test.execute()
            self.test.cleanup()
            self.result = 100
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
        self.__logger.info("Generate Test report")
        self.test.reports_collection.generate_report()
