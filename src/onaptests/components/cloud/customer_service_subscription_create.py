from onapsdk.aai.business import Customer
from onapsdk.service import Service
from onapsdk.configuration import settings

from ..base import BaseComponent
from .customer_create import CustomerCreateComponent


class CustomerServiceSubscriptionCreateComponent(BaseComponent):

    def __init__(self, cleanup=False):
        super().__init__(cleanup=cleanup)
        self.add_subcomponent(CustomerCreateComponent(cleanup=cleanup))

    def action(self):
        service = Service(name=settings.SERVICE_NAME)
        customer = Customer.get_by_global_customer_id(settings.GLOBAL_CUSTOMER_ID)
        customer.subscribe_service(service)
