"""Base step that runs a PNF simulator."""
from onaptests.steps.simulator.pnf import utils
from onaptests.steps.base import BaseStep

class PNFInstanceStep(BaseStep):
    """Run PNF simulator containers."""

    @property
    def description(self) -> str:
        """Step description."""
        return "Run PNF simulator containers."

    @property
    def component(self) -> str:
        """Component name."""
        return "Environment"

    @BaseStep.store_state
    def execute(self) -> None:
        """Run PNF simulator containers."""
        utils.build_image()
        utils.bootstrap_simulator()
        utils.run_container()

    def cleanup(self) -> None:
        """Remove containers and images."""
        utils.stop_container()
        utils.remove_simulator()
        utils.remove_image()
