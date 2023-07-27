#!/usr/bin/env python
"""Simple CDS blueprint erichment test scenario."""
from onapsdk.configuration import settings
from onaptests.scenario.scenario_base import ScenarioBase
from onaptests.steps.onboard.cds import CbaEnrichStep


class CDSBlueprintEnrichment(ScenarioBase):
    """Enrich simple blueprint using CDS blueprintprocessor."""

    def __init__(self, **kwargs):
        """Init CDS blueprint enrichment use case."""
        super().__init__('basic_cds', **kwargs)
        self.test = CbaEnrichStep(
            cleanup=settings.CLEANUP_FLAG)
