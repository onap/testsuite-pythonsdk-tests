from onapsdk.aai.business import Customer
from onapsdk.sdc.service import Service
from onapsdk.configuration import settings

from ..base import BaseStep
from .customer_create import CustomerCreateStep


class CustomerServiceSubscriptionCreateStep(BaseStep):

    def __init__(self, cleanup=False):
        super().__init__(cleanup=cleanup)
        self.add_step(CustomerCreateStep(cleanup=cleanup))

    def execute(self):
        service = Service(name=settings.SERVICE_NAME)
        customer = Customer.get_by_global_customer_id(settings.GLOBAL_CUSTOMER_ID)
        customer.subscribe_service(service)
