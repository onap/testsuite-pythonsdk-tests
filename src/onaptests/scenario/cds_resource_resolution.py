#!/usr/bin/env python
"""CDS resource resolution test scenario."""
from onaptests.scenario.scenario_base import BaseStep, ScenarioBase, BaseScenarioStep
from onaptests.steps.onboard.cds import CbaProcessStep
from onaptests.steps.simulator.cds_mockserver import \
    CdsMockserverCnfConfigureStep


class CDSResourceResolutionStep(BaseScenarioStep):
    """Step created to run scenario and generate report."""

    def __init__(self):
        """Initialize step.

        Substeps:
            - CdsMockserverCnfConfigureStep,
            - CbaProcessStep.
        """
        super().__init__(cleanup=BaseStep.HAS_NO_CLEANUP)
        self.add_step(CdsMockserverCnfConfigureStep())
        self.add_step(CbaProcessStep())

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
        return "TEST"


class CDSResourceResolution(ScenarioBase):
    """Enrich simple blueprint using CDS blueprintprocessor."""

    def __init__(self, **kwargs):
        """Init CDS resource resolution use case."""
        super().__init__('basic_cds', **kwargs)
        self.test = CDSResourceResolutionStep()
