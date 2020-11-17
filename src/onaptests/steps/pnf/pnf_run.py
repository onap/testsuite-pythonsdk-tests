"""Base step that runs a PNF simulator."""
import os
from typing import Optional

from onaptests.configuration import settings
from onaptests.steps.pnf.simulator_source import utils
from onaptests.steps.base import BaseStep

class PNFSimulator(BaseStep):
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
        old_pwd = switch_workdir()
        utils.build_image()
        utils.bootstrap_simulator(**settings.PNF_VES_CONFIG)
        utils.run_container()
        switch_workdir(old_pwd)

    @BaseStep.store_state
    def cleanup(self) -> None:
        """Remove simulators and images."""

        old_pwd = switch_workdir()
        utils.stop_container()
        utils.remove_simulator()
        utils.remove_image()
        switch_workdir(old_pwd)

        super().cleanup()

def switch_workdir(back_pwd: str = None) -> Optional[str]:
    """Switch work directory temporarily for PNF simulator operations.

    When `back_pwd` path is provided, it means go back tp the repository
    you came from.

    Arguments:
        back_pwd: path to go back to.

    """
    old_pwd = os.getcwd()

    if not back_pwd:
        curr_pwd =  (
            f"{os.path.dirname(os.path.realpath(__file__))}"
            f"/simulator_source"
            )
    else:
        curr_pwd = back_pwd

    os.chdir(curr_pwd)
    return old_pwd
