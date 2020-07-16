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

from onaptests.actions.onboard import Onboard
from onaptests.actions.instantiate import Instantiate
from onaptests.actions.delete import Delete
from onaptests.actions.cloudresources import CloudResources

class Scenario:
    """class defining the different scenarios."""

    def __init__(self, **kwargs):
        """Initialize E2E object."""

        super().__init__()

        if "type" in kwargs:
            self.scenario_name = kwargs['type']
        else:
            raise ValueError("Service Name to specify")

    @staticmethod
    def onboard(service_name):
        service = Onboard(service_name=service_name)
        return service.onboard_resources()

    @staticmethod
    def add_cloud_resources():
        cloud = CloudResources()
        cloud.add_cloud_resources()
        return cloud

    @staticmethod
    def instantiate(instance_name, cloud_resources, service=None, service_name=None):
        if service:
            service_name = service.name
        instant = Instantiate(service_name=service_name,
                              instance_name=instance_name)
        return instant.instantiate(cloud_resources, service)

    @staticmethod
    def clean(service_name, service_instance_name=None, service_instance=None):
        if service_instance:
            clean_object = Delete(service_name=service_name,
                                  instance_name=service_instance.name)
            clean_object.delete(service_instance)
        else:
            if service_instance_name:
                clean_object = Delete(service_name=service_name,
                                      instance_name=service_instance_name)
                clean_object.delete()
            else:
                raise ValueError("No service_instance_name nor service_instance provided")

    def e2e(self, delete=True):
        """E2E steps"""
        service = self.onboard(self.scenario_name)
        cloud = self.add_cloud_resources()
        instance_name = self.scenario_name + "-" + str(uuid4())

        service_instance = self.instantiate(instance_name, cloud, service)
        if delete:
            self.clean(self.scenario_name,
                       service_instance=service_instance)
