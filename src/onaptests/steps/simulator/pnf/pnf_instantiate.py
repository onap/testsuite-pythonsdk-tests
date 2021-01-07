"""Base step that runs a PNF simulator."""
from onaptests.steps.base import BaseStep

class PNFInstanceStep(BaseStep):
    """Run PNF simulator."""

    @property
    def description(self) -> str:
        """Step description."""
        return "Run PNF simulator."

    @property
    def component(self) -> str:
        """Component name."""
        return "Environment"

    @BaseStep.store_state
    def execute(self) -> None:
        """Run PNF simulator."""

    def cleanup(self) -> None:
        """Stop simulator."""
