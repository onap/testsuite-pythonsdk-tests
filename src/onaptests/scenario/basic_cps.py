#!/usr/bin/env python
"""Basic CPS test case."""
from onapsdk.configuration import settings

from onaptests.scenario.scenario_base import (BaseScenarioStep, BaseStep,
                                              ScenarioBase)
from onaptests.steps.onboard.cps import (CheckPostgressDataBaseConnectionStep,
                                         QueryCpsAnchorNodeStep)


class BasicCpsStep(BaseScenarioStep):
    """Main basic cps scenario step."""

    def __init__(self):
        """Initialize step.

        Substeps:
            - QueryCpsAnchorNodeStep
            - CheckPostgressDataBaseConnectionStep.
        """
        super().__init__(cleanup=BaseStep.HAS_NO_CLEANUP)
        self.add_step(QueryCpsAnchorNodeStep())
        if settings.CHECK_POSTGRESQL:
            self.add_step(CheckPostgressDataBaseConnectionStep())

    @property
    def description(self) -> str:
        """Step description.

        Used for reports

        Returns:
            str: Step description

        """
        return "Basic CPS scenario step"

    @property
    def component(self) -> str:
        """Component name.

        Name of component which step is related with.
            Most is the name of ONAP component.

        Returns:
            str: Component name

        """
        return "TEST"


class BasicCps(ScenarioBase):
    """Create CPS resources:
            - dataspace
            - schemaset
            - anchor
            - node
        Update and Query on node
        And check PostgreSQL connection. Use bookstore YANG model (available on CPS repository
        https://github.com/onap/cps/blob/master/cps-service/src/test/resources/bookstore.yang).
        At the end delete what's available to be deleted.

    """

    def __init__(self, **kwargs):
        """Init Basic CPS."""
        super().__init__('basic_cps', **kwargs)
        self.test = BasicCpsStep()
