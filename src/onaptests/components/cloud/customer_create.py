from onapsdk.aai.business import Customer
from onapsdk.configuration import settings

from ..base import BaseComponent


class CustomerCreateComponent(BaseComponent):

    def action(self):
        Customer.create(settings.GLOBAL_CUSTOMER_ID, settings.GLOBAL_CUSTOMER_ID, "INFRA")
