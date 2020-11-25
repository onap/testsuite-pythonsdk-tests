"""Base step that runs a PNF simulator."""
from onaptests.steps.simulator.pnf import utils
from onaptests.configuration import settings
from onaptests.steps.base import BaseStep

class PNFSimulatorStep(BaseStep):
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
        """Run PNF simulator containers.

        Use settings values:
         - PNF_VES_CONFIG

        """
        super().execute()
        utils.build_image()
        utils.bootstrap_simulator(**settings.PNF_VES_CONFIG)
        utils.run_container()

    @BaseStep.store_state
    def cleanup(self) -> None:
        """Remove simulators and images."""
        utils.stop_container()
        utils.remove_simulator()
        utils.remove_image()
        super().cleanup()
