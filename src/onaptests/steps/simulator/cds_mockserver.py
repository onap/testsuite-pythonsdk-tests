# http://www.apache.org/licenses/LICENSE-2.0
"""CDS mockserver registration module."""

import time
from typing import Any, Dict

import requests
from onapsdk.configuration import settings

from onaptests.steps.base import BaseStep
from onaptests.steps.instantiate.msb_k8s import CreateInstanceStep
from onaptests.utils.exceptions import EnvironmentPreparationException, OnapTestException


class CdsMockserverCnfConfigureStep(BaseStep):
    """Configure cds mockserver expectations."""

    def __init__(self, cleanup: bool = False) -> None:
        """Initialize step.

        Substeps:
            - CreateInstanceStep.
        """
        super().__init__(cleanup=cleanup)
        self.add_step(CreateInstanceStep(cleanup=cleanup))

    @property
    def description(self) -> str:
        """Step description."""
        return "Configure cds-mockserver."

    @property
    def component(self) -> str:
        """Component name."""
        return "Environment"

    @BaseStep.store_state
    def execute(self) -> None:
        """Create mockserver expectations.

        Use settings values:
         - CDS_MOCKSERVER_EXPECTATIONS.
        """
        super().execute()
        time.sleep(60)  # Wait for mockserver
        for expectation in settings.CDS_MOCKSERVER_EXPECTATIONS:
            try:
                response = requests.put(
                    "http://portal.api.simpledemo.onap.org:30726/mockserver/expectation",
                    json={
                        "httpRequest" : {
                            "method": expectation["method"],
                            "path": expectation["path"]
                        },
                        "httpResponse" : {
                            "body": expectation["response"]
                        }
                    }
                )
                response.raise_for_status()
            except (requests.ConnectionError, requests.HTTPError) as http_error:
                self._logger.debug(f"Can't register cds-mockserver expectation: {str(http_error)}")
                raise OnapTestException("CDS mockserver not configured")
