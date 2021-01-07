"""Base step that runs a PNF simulator."""
from onaptests.steps.base import BaseStep
from onaptests.steps.simulator.pnf.pnf_instantiate import PNFInstanceStep

class PNFRegisterStep(BaseStep):
    """Run PNF simulator containers."""

    def __init__(self, cleanup=True):
        """Initialize step.

        Substeps:
            - PNFInstanceStep

        """
        super().__init__(cleanup=cleanup)
        self.add_step(PNFInstanceStep(cleanup=cleanup))

    @property
    def description(self) -> str:
        """Step description."""
        return "Register PNF with VES."

    @property
    def component(self) -> str:
        """Component name."""
        return "Environment"

    @BaseStep.store_state
    def execute(self) -> None:
        """Register with VES."""
        super().execute()

    @BaseStep.store_state
    def cleanup(self) -> None:
        """Substeps cleanup - no unregister."""
        super().cleanup()
