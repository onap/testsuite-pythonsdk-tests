#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
"""Clamp Scenario class."""
from onapsdk.clamp.clamp_element import Clamp
from onapsdk.sdc.service import Service

from onaptests.configuration import settings
from onaptests.actions.onboard_clamp import OnboardClamp
from onaptests.actions.instantiate_loop import InstantiateLoop


class ClampScenario():
    """class defining the different CLAMP scenarios."""

    count: int = 0

    def __init__(self, **kwargs):
        """Initialize CLAMP scenario."""
        if "service_name" in kwargs:
            self.service_name = kwargs['service_name']
        else:
            raise ValueError("Service Name to specify")
        Service.set_proxy({ 'http': settings.SOCK_HTTP, 'https': settings.SOCK_HTTP})
        Clamp.set_proxy({ 'http': settings.SOCK_HTTP, 'https': settings.SOCK_HTTP})
        #must change cert path in python-onapsdk configuration
        Clamp.create_cert()

    @property
    def service(self):
        """Look for the service."""
        return Service(name=self.service_name)

    def onboard_service_artifact(self):
        """Create and distribute a service with blueprint artifact."""
        service = OnboardClamp(service_name=self.service_name)
        return service.onboard_artifact()

    def check(self, operational_policies: list, is_template: bool = False) -> str:
        """Check CLAMP requirements to create a loop."""
        for policy in operational_policies:
            exist = Clamp.check_policies(policy_name=policy["name"],                          
                                         req_policies=30)# 30 required policy
            if not exist:
                raise ValueError("Couldn't load the policy %s", policy)
        if is_template:
            loop_template = Clamp.check_loop_template(service=self.service)
            return loop_template

    @staticmethod
    def instantiate_clamp(loop_template: str, loop_name: str, operational_policies: list):
        """Instantite a closed loopin CLAMP."""
        loop = InstantiateLoop(template=loop_template,       
                               loop_name=loop_name,
                               operational_policies=operational_policies)
        return loop.instantiate_loop()

    def loop_counter(self, action: str) -> None:
        """ Count number of loop instances."""
        if  action == "plus":
            self.count += 1
        if  action == "minus":
            self.count -= 1

    def e2e(self, operational_policies: list, delete: bool = True):
        """E2E steps"""
        #service = self.onboard_service_artifact()
        # Test 1
        loop_template = self.check(operational_policies, True)
        # Test 2
        loop_name = "loop_instance_" + str(self.count)
        self.loop_counter(action="plus")
        loop_instance = self.instantiate_clamp(loop_template=loop_template,
                                               loop_name=loop_name,
                                               operational_policies=operational_policies)
        if delete:
            self.loop_counter(action="minus")
            loop_instance.delete()
