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

        old_pwd = self.switch_workdir()

        utils.build_image()
        utils.bootstrap_simulator(**settings.PNF_VES_CONFIG)
        utils.run_container()

        self.switch_workdir(old_pwd)

    BaseStep.store_state
    def cleanup(self) -> None:
        """Remove simulators and images."""

        old_pwd = self.switch_workdir()

        utils.stop_container()
        utils.remove_simulator()
        utils.remove_image()

        self.switch_workdir(old_pwd)

        super().cleanup()

    def switch_workdir(self, back: str = None) -> Optional[str]:
        """Switch work directory temporarily for PNF simulator operations"""
        if not back:
            old_pwd = os.getcwd()
            curr_dir = os.path.dirname(os.path.realpath(__file__)) + "/simulator_source"
            os.chdir(curr_dir)
            return old_pwd

        os.chdir(back)
