from onapsdk.aai.business import Customer
from onapsdk.configuration import settings

from ..base import BaseStep


class CustomerCreateStep(BaseStep):
    """Customer creation step."""

    @BaseStep.store_state
    def execute(self):
        """Create cutomer.

        Use settings values:
         - GLOBAL_CUSTOMER_ID.
        """
        Customer.create(settings.GLOBAL_CUSTOMER_ID, settings.GLOBAL_CUSTOMER_ID, "INFRA")
