"""Base step that runs a PNF simulator."""
import time
import urllib.parse

from onapsdk.configuration import settings

from onaptests.steps.pnf import utils
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
        sim_settings: dict = settings.PNF_VES_CONFIG
        ves_url = urllib.parse.urlparse(settings.VES_URL)
        sim_settings["vesip"] = ves_url.hostname
        sim_settings["vesport"] = ves_url.port
        utils.bootstrap_simulator(**sim_settings)
        utils.run_container()
        self._logger.info("Wait 5 seconds for simulator")
        time.sleep(5)
        utils.register(config=settings.PNF_VES_CONFIG, data=settings.PNF_CUSTOM_DATA)

    @BaseStep.store_state
    def cleanup(self) -> None:
        """Remove simulators and images."""
        utils.stop_container()
        utils.remove_simulator()
        utils.remove_image()
        super().cleanup()
