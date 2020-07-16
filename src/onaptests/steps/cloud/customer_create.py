from onapsdk.aai.business import Customer
from onapsdk.configuration import settings

from ..base import BaseStep


class CustomerCreateStep(BaseStep):

    def execute(self):
        Customer.create(settings.GLOBAL_CUSTOMER_ID, settings.GLOBAL_CUSTOMER_ID, "INFRA")
