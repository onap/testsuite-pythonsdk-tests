from onapsdk.aai.business import Customer
from onapsdk.configuration import settings
from onapsdk.exceptions import APIError

from ..base import BaseStep


class CustomerCreateStep(BaseStep):
    """Customer creation step."""

    @property
    def description(self) -> str:
        """Step description."""
        return "Create customer."

    @property
    def component(self) -> str:
        """Component name."""
        return "AAI"

    @BaseStep.store_state
    def execute(self):
        """Create cutomer.

        Use settings values:
         - GLOBAL_CUSTOMER_ID.
        """
        super().execute()
        try:
            Customer.create(settings.GLOBAL_CUSTOMER_ID, settings.GLOBAL_CUSTOMER_ID, "INFRA")
        except APIError:
            self._logger.warn("Try to update the Customer failed.")
