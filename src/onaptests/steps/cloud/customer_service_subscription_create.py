from onapsdk.aai.business import Customer
from onapsdk.configuration import settings
from onapsdk.sdc.service import Service

from ..base import BaseStep
from .customer_create import CustomerCreateStep


class CustomerServiceSubscriptionCreateStep(BaseStep):
    """Cutomer service subsription creation step"""

    def __init__(self):
        """Initialize step.

        Substeps:
            - CustomerCreateStep.
        """
        super().__init__(cleanup=BaseStep.HAS_NO_CLEANUP)
        self.add_step(CustomerCreateStep())

    @property
    def description(self) -> str:
        """Step description."""
        return "Create customer's service subscription."

    @property
    def component(self) -> str:
        """Component name."""
        return "AAI"

    @BaseStep.store_state
    def execute(self):
        """Create customer service subsription.

        Use settings values:
         - GLOBAL_CUSTOMER_ID,
         - SERVICE_NAME.
        """
        super().execute()
        service = Service(name=settings.SERVICE_NAME)
        customer = Customer.get_by_global_customer_id(settings.GLOBAL_CUSTOMER_ID)
        customer.subscribe_service(service.name)
