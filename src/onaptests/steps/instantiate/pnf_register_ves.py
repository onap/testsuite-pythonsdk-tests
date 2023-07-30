# http://www.apache.org/licenses/LICENSE-2.0
"""PNF simulator registration module."""

import time

import requests
from jinja2 import Environment, PackageLoader, select_autoescape
from onapsdk.configuration import settings
from onapsdk.ves.ves import Ves

from onaptests.steps.base import BaseStep
from onaptests.steps.cloud.expose_service_node_port import \
    ExposeServiceNodePortStep
from onaptests.utils.exceptions import OnapTestException


class SendPnfRegisterVesEvent(BaseStep):
    """PNF VES registration step."""

    def __init__(self) -> None:
        """Initialize step."""
        super().__init__()
        if settings.EXPOSE_SERVICES_NODE_PORTS:
            self.add_step(ExposeServiceNodePortStep(component="VES-Collector",
                service_name="dcae-ves-collector", port=8080, node_port=settings.VES_NODE_PORT))
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
        """Send PNF registration event."""
        super().execute()
        registration_number: int = 0

        source_name = settings.SERVICE_INSTANCE_NAME
        jinja_env = Environment(autoescape=select_autoescape(['jinja']),
                                loader=PackageLoader('onaptests.templates',
                                                     'artifacts'))
        template = jinja_env.get_template("pnf_register_ves_message.jinja")
        event_data = template.render(
            source_name=source_name)

        registered_successfully: bool = False
        while (registration_number < settings.PNF_REGISTRATION_NUMBER_OF_TRIES and
               not registered_successfully):
            try:
                response = Ves.send_event(version="v7", json_event=event_data,
                                          basic_auth=settings.VES_BASIC_AUTH)
                if response is None:
                    raise OnapTestException("Failed to send event to VES SERVER")
                response.raise_for_status()
                registered_successfully = True
                self._logger.info(f"PNF registered with {settings.SERVICE_INSTANCE_NAME} "
                                  "source name")
            except (requests.ConnectionError, requests.HTTPError) as http_error:
                self._logger.debug(f"Can't send to ves: {str(http_error)}")
                registration_number += 1
                time.sleep(settings.PNF_WAIT_TIME)
        if not registered_successfully:
            raise OnapTestException("PNF not registered successfully")
