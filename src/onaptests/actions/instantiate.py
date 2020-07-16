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
"""Instantiation class."""
import time
import sys

from onapsdk.configuration import settings


from onapsdk.aai.business import Customer
from onapsdk.so.instantiation import (
    ServiceInstantiation,
    VnfParameter
)
from onapsdk.sdc.service import Service

from onaptests.actions.common import Common

class Instantiate(Common):
    """
    Class to automate the instantiation of a service including VNF and VF

    It is assumed that the Design phase has been already done
    The yaml template is available and stored in the template directory
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
        self.vf_list = []
        self.customer = None
        self.service_subscription = None

    def create_customer(self, customer_id):
        """Create customer if it does not exist."""
        self.logger.info("******** Create Customer *******")
        customer = None
        for found_customer in list(Customer.get_all()):
            self.logger.debug("Customer %s found", found_customer.subscriber_name)
            if found_customer.subscriber_name == customer_id:
                self.logger.info("Customer %s found", found_customer.subscriber_name)
                customer = found_customer
                break
        if not customer:
            customer = Customer.create(
                customer_id,
                customer_id,
                "INFRA")
        return customer

    def declare_service_subscription(self, customer, service):
        """Declare service subscription if not created."""
        self.logger.info("******** Check Service Subscription *******")
        service_subscription = None
        for service_sub in customer.service_subscriptions:
            self.logger.debug("Service subscription %s is found", service_sub.service_type)
            if service_sub.service_type == service.name:
                self.logger.info("Service %s subscribed", service.name)
                service_subscription = service_sub
                break

        if not service_subscription:
            self.logger.info("******** Subscribe Service *******")
            service_subscription = customer.subscribe_service(service)
        return service_subscription

    def check_tenant_exists(self, cloud_region, tenant_name):
        """Check if tenant exists."""
        tenant = None
        for found_tenant in cloud_region.tenants:
            self.logger.debug("Tenant %s found in %s_%s", found_tenant.name,
                              cloud_region.cloud_owner,
                              cloud_region.cloud_region_id)
            if found_tenant.name == tenant_name:
                self.logger.info("Found my Tenant %s", found_tenant.name)
                tenant = found_tenant
                break
        if not tenant:
            self.logger.error("tenant %s not found", tenant_name)
            sys.exit(1)
        return tenant

    def get_vnf_parameters(self, service_name):
        """ get vnf parameters from vnf service yaml file."""
        vnf_params = []
        vnfparams = self.get_vnf_parameters_from_sdnc(service_name, service_name)
        self.logger.debug("VNF parameters are %s", vnfparams)
        for params in vnfparams:
            vnf_params.append(VnfParameter(name=params['name'], value=params['value']))

        return vnf_params

    def find_service_sdc(self, service_name):
        """ Find service in SDC, check distribution."""
        self.logger.info("******** Find Service in SDC *******")
        service = None
        services = Service.get_all()
        for found_service in services:
            self.logger.debug("Service %s is found, distribution %s",
                              found_service.name,
                              found_service.distribution_status)
            if found_service.name == service_name:
                self.logger.info("Found Service %s in SDC", found_service.name)
                service = found_service
                break
        return service

    def check_service_distribution(self, service, try_max, wait_time):
        """ Check service distribution is complete."""
        self.logger.info("*Check if service is completly distributed *")
        nb_try = 0
        service_distributed = False
        while service_distributed is False and nb_try < try_max:
            if service.distributed:
                self.logger.info("******** Service %s is now distributed *******",
                                 service.name)
                service_distributed = True
                break
            self.logger.info("Service %s distribution not complete, status %s wait 10s",
                             service.name,
                             service.distribution_status)
            time.sleep(wait_time)
            nb_try += 1
        if not service_distributed:
            self.logger.error("Service %s not distributed", service.name)
            sys.exit(1)

    def check_service_instance_exists(self, service_subscription, instance_name):
        """ Check if service_instance already exists."""
        service_instance = None
        for service_element in service_subscription.service_instances:
            if service_element.instance_name == instance_name:
                service_instance = service_element
                self.logger.debug("Service instance_name found %s ", service_element.instance_name)
                break
        return service_instance

    def check_service_instantiation(self, service_subscription, instance_name):
        """ Check if service is now intantiated."""
        service_instance = self.check_service_instance_exists(
            service_subscription,
            instance_name)
        if not service_instance:
            self.logger.error("******** Service %s instantiation failed", instance_name)
            sys.exit(1)
        return service_instance

    def check_service_instance_active(self, service_instance, wait_time, try_max):
        """Check if service instance is active."""
        nb_try = 0
        service_active = False
        while service_active is False and nb_try < try_max:
            if service_instance.orchestration_status == "Active":
                self.logger.info("******** Service Instance %s is active *******",
                                 service_instance.name)
                service_active = True
                break
            self.logger.info("Service %s instantiation not complete, Status: %s, wait 10s",
                             service_instance.name,
                             service_instance.orchestration_status)
            time.sleep(wait_time)
            nb_try += 1
        return service_active

    #  pylint: disable=too-many-arguments
    def instantiate_service(self,
                            instance_name,
                            service,
                            service_subscription,
                            cloud_region,
                            tenant,
                            customer,
                            owning_entity,
                            project,
                            try_max=10,
                            wait_time1=120,
                            wait_time2=10):
        """ Instantiate service."""
        self.logger.info("******** Instantiate Service *******")
        service_instance = self.check_service_instance_exists(
            service_subscription,
            instance_name)
        if not service_instance:
            self.logger.info("******** Service Instance not existing: Instantiate *******")
            # Instantiate service
            ServiceInstantiation.instantiate_so_ala_carte(
                service,
                cloud_region,
                tenant,
                customer,
                owning_entity,
                project,
                service_instance_name=instance_name
            )
            time.sleep(wait_time1)
        else:
            self.logger.info("******** Service Instance already existing *******")

        service_instance = self.check_service_instantiation(
            service_subscription,
            instance_name)

        service_active = self.check_service_instance_active(
            service_instance,
            wait_time2,
            try_max)

        if service_active is False:
            self.logger.error("Service %s instantiation failed", service_instance.name)
            sys.exit(1)
        return service_instance

    def add_vnf_to_service(self, service_instance, platform, line_of_business, wait_time=10):
        """ Add vnf to instantiated service."""

        self.logger.info("******** Get VNFs in Service Model *******")
        vnfs = service_instance.service_subscription.sdc_service.vnfs

        self.logger.info("******** Create VNFs *******")
        for vnf in vnfs:
            self.logger.debug("Check if VNF instance of class %s exist", vnf.name)
            vnf_found = False
            for vnf_instance in service_instance.vnf_instances:
                self.logger.debug("VNF instance %s checked in Service Instance ",
                                  vnf_instance.vnf_name)
                if vnf_instance.vnf_name == vnf.name:
                    self.logger.debug("VNF instance %s found in Service Instance ",
                                      vnf_instance.vnf_name)
                    vnf_found = True
                    break
            if vnf_found is False:
                vnf_instantiation = service_instance.add_vnf(vnf, line_of_business, platform)
                while not vnf_instantiation.finished:
                    self.logger.debug("Wait for VNF %s instantiation", vnf.name)
                    time.sleep(wait_time)

    def instantiate_vf_modules(self, service_instance, service_name):
        """Add Vf modules for each vnf."""
        for vnf_instance in service_instance.vnf_instances:
            self.logger.debug("VNF instance %s found in Service Instance ", vnf_instance.name)
            self.logger.info("******** Get VfModules in VNF Model *******")
            vf_module = vnf_instance.vnf.vf_module

            self.logger.info("******** Create VF Module %s *******", vf_module.name)
            vnf_parameters = self.get_vnf_parameters(service_name)
            vf_module_instantiation = vnf_instance.add_vf_module(
                vf_module,
                vnf_parameters=vnf_parameters)
            nb_try = 0
            nb_try_max = 30
            while not vf_module_instantiation.finished and nb_try < nb_try_max:
                self.logger.info("Wait for vf module instantiation")
                nb_try += 1
                time.sleep(20)
            if vf_module_instantiation.finished:
                self.logger.info("VfModule %s instantiated", vf_module.name)
            else:
                self.logger.error("VfModule instantiation %s failed", vf_module.name)

    def instantiate(self, cloud_resources, service=None,):
        """Instantiate a Service with ONAP.

        The instantiation consists in the different steps:
          * Create the customer in AAI
          * Retrieve Service from SDC
          * Declare subcription, link to tenant in AAI
          * Instantiate the service instance (SO)
          * Create the VNF instance (SO)
          * preload the VNF parameters in the SDNC
          * Create the VF module instance (SO)
        """
        customer = self.create_customer(settings.GLOBAL_CUSTOMER_ID)
        if not service:
            service = self.find_service_sdc(self.service_name)
        self.check_service_distribution(service, 10, 10)
        self.logger.info("******** AAI declaration *******")
        service_subscription = self.declare_service_subscription(
            customer,
            service)
        tenant = self.check_tenant_exists(
            cloud_resources.cloud_region,
            settings.TENANT_NAME)
        service_subscription.link_to_cloud_region_and_tenant(
            cloud_resources.cloud_region,
            tenant)

        service_instance = self.instantiate_service(
            self.instance_name,
            service,
            service_subscription,
            cloud_resources.cloud_region,
            tenant,
            customer,
            cloud_resources.owning_entity,
            cloud_resources.project)

        self.add_vnf_to_service(
            service_instance,
            cloud_resources.platform,
            cloud_resources.line_of_business)
        self.instantiate_vf_modules(
            service_instance,
            self.service_name)
        return service_instance
