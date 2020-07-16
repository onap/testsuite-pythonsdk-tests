#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
#  pylint: disable=missing-docstring
"""E2E class."""
from uuid import uuid4

from onaptests.scenario.scenario import Scenario
from onaptests.scenario.onboard import Onboard
from onaptests.scenario.instantiate import Instantiate
from onaptests.scenario.delete import Delete

class E2E(Scenario):
    """E2E class to onboard and instantiate."""

    def __init__(self, **kwargs):
        """Initialize E2E object."""

        super().__init__()

        if "service_name" in kwargs:
            self.service_name = kwargs['service_name']
        else:
            raise ValueError("Service Name to specify")

    @staticmethod
    def onboard_e2e_service(service_name):
        service = Onboard(service_name=service_name)
        return service.onboard_resources()

    @staticmethod
    def instantiate_e2e_service(service, instance_name):
        instant = Instantiate(service_name=service.name,
                              instance_name=instance_name)
        return instant.instantiate(service)

    @staticmethod
    def remove(service_name, service_instance):
        service = Delete(service_name=service_name,
                         instance_name=service_instance.name)
        service.delete(service_instance)

    def e2e(self, delete=True):
        """E2E steps"""
        service = self.onboard_e2e_service(self.service_name)
        instance_name = self.service_name + "-" + str(uuid4())
        service_instance = self.instantiate_e2e_service(service, instance_name)
        if delete:
            self.remove(self.service_name, service_instance)
