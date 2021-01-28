"""Start simulators via simulators' API."""
from typing import Union, Optional, Dict
import requests
from onaptests.steps.base import BaseStep
from onaptests.utils.exceptions import TestConfigurationException

class SimulatorStartStep(BaseStep):
    """Basic operations on a docker container."""

    def __init__(self,  # pylint: disable=R0913
                 cleanup: bool = False,
                 https: bool = False,
                 host: str = None,
                 port: Union[int, str] = None,
                 endpoint: Optional[str] = "",
                 method: str = "GET",
                 data: Dict = None) -> None:
        """Prepare request data and details.

        Arguments:
            cleanup (bool):
                determines if cleanup action should be called.
                Defaults to False.
            https (bool): use https or http. Defaults to False.
            host (str): IP or hostname. Defaults to None.
            port (Union[int, str]): port number. Defaults to None.
            endpoint (str):
                additional endpoint if applicable.
                Defautls to "".
            method (str):
                GET or POST strings, case insensitive.
                Defaults tp GET.
            data (Dict):
                parameters, that request's post() or get() takes, besides url.
                For example, {"json": {}, ...}. Defaults to None.
        """
        if not host and not port:
            raise TestConfigurationException("Provide host and/or port.")

        super().__init__(cleanup=cleanup)

        default_port = "443" if https else "80"
        protocol = "https" if https else "http"
        endpoint = endpoint[1:] if endpoint.startswith("/") else endpoint

        self.method = method
        self.data = data if data else {}
        self.url = f"{protocol}://{host}:{port or default_port}/{endpoint}"

    @property
    def description(self) -> str:
        """Step description."""
        return "Send commands to the simulator application."

    @property
    def component(self) -> str:
        """Component name."""
        return "Environment"

    @BaseStep.store_state
    def execute(self) -> None:
        """Send a start command to the simulator application."""
        super().execute()
        requests.request(self.method.upper(), self.url, **self.data)
