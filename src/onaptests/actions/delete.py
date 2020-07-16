#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
#  pylint: disable=duplicate-code
#  pylint: disable=missing-docstring
#  pylint: disable=too-many-branches
#  pylint: disable=too-many-public-methods
"""Delete class."""
import sys
import time
from onapsdk.aai.business import Customer
from onapsdk.configuration import settings
from onaptests.actions.common import Common

class Delete(Common):
    """
    Class to automate the deletion of a Service including VNF and VF.

    """

    def __init__(self, **kwargs):
        """Initialize Solution object."""
        super().__init__()

        if "service_name" in kwargs:
            self.service_name = kwargs['service_name']
        else:
            raise ValueError("Service Name to define")

        if "instance_name" in kwargs:
            self.instance_name = kwargs['instance_name']
        else:
            self.instance_name = self.service_name

    def get_customer(self):
        """Get customer if it does not exist."""
        self.logger.info("******** Get Customer *******")
        customer = None
        for found_customer in list(Customer.get_all()):
            self.logger.debug("Customer %s found", found_customer.subscriber_name)
            if found_customer.subscriber_name == settings.GLOBAL_CUSTOMER_ID:
                self.logger.info("Customer %s found", found_customer.subscriber_name)
                customer = found_customer
                break
        if not customer:
            self.logger.error("Customer %s not found", settings.GLOBAL_CUSTOMER_ID)
        return customer

    def get_service_subscription(self, customer, service_name):
        """Get Service Subscription"""
        self.logger.info("******** Get Service Subscription *******")
        service_subscription = None
        for service_sub in customer.service_subscriptions:
            self.logger.debug("Service subscription %s is found", service_sub.service_type)
            if service_sub.service_type == service_name:
                self.logger.info("Service %s subscribed", service_name)
                service_subscription = service_sub
                break
        if not service_subscription:
            self.logger.error("Service subcription for service %s not found", service_name)
            sys.exit(1)
        return service_subscription

    def get_service_instance(self, service_subscription, instance_name):
        """Get Service Instance"""

        self.logger.info("******** Get Service Instance *******")
        service_instance = None
        for serv_element in service_subscription.service_instances:
            if serv_element.instance_name == instance_name:
                service_instance = serv_element
                break
        if not service_instance:
            self.logger.error("******** Service Instance not existing *******")
            sys.exit(1)
        return service_instance

    def delete(self, service_instance=None):
        """Delete a service based on its service name."""
        customer = self.get_customer()
        if not service_instance:
            service_subscription = self.get_service_subscription(customer, self.service_name)
            service_instance = self.get_service_instance(service_subscription, self.instance_name)
        self.logger.info("*******************************")
        self.logger.info("**** SERVICE DELETION *********")
        self.logger.info("*******************************")
        for vnf_instance in service_instance.vnf_instances:
            self.logger.debug("VNF instance %s found in Service Instance ",
                              vnf_instance.name)
            self.logger.info("******** Get VF Modules *******")
            for vf_module in vnf_instance.vf_modules:
                self.logger.info("******** Delete VF Module %s *******",
                                 vf_module.name)
                vf_module_deletion = vf_module.delete()
                nb_try = 0
                nb_try_max = 30
                while not vf_module_deletion.finished and nb_try < nb_try_max:
                    self.logger.info("Wait for vf module deletion")
                    nb_try += 1
                    time.sleep(20)
                if vf_module_deletion.finished:
                    self.logger.info("VfModule %s deleted", vf_module.name)
                else:
                    self.logger.error("VfModule deletion %s failed", vf_module.name)
                    sys.exit(1)
            self.logger.info("******** Delete VNF %s *******", vnf_instance.name)
            vnf_deletion = vnf_instance.delete()
            nb_try = 0
            nb_try_max = 30
            while not vnf_deletion.finished and nb_try < nb_try_max:
                self.logger.info("Wait for vnf deletion")
                nb_try += 1
                time.sleep(15)
            if vnf_deletion.finished:
                self.logger.info("VNF %s deleted", vnf_instance.name)
            else:
                self.logger.error("VNF deletion %s failed", vnf_instance.name)
                sys.exit(1)
        self.logger.info("******** Delete Service %s *******", service_instance.name)
        service_deletion = service_instance.delete()
        nb_try = 0
        nb_try_max = 30
        while not service_deletion.finished and nb_try < nb_try_max:
            self.logger.info("Wait for Service deletion")
            nb_try += 1
            time.sleep(15)
        if service_deletion.finished:
            self.logger.info("Service %s deleted", service_instance.name)
        else:
            self.logger.error("Service deletion %s failed", service_instance.name)
            sys.exit(1)
