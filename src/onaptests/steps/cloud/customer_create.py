from onapsdk.aai.business import Customer
from onaptests.configuration import settings

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
        Customer.create(settings.GLOBAL_CUSTOMER_ID, settings.GLOBAL_CUSTOMER_ID, "INFRA")
