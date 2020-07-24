#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
"""E2E closed loop class."""
import time

from onapsdk.clamp.clamp_element import Clamp
from onapsdk.clamp.loop_instance import LoopInstance
from onapsdk.sdc.service import Service

from onaptests.scenario.clamp_scenario import ClampScenario
from onaptests.actions.onboard_clamp import OnboardClamp
from onaptests.actions.instantiate_loop import InstantiateLoop


class ClosedLoop(ClampScenario):
     """Closed Loop class to onboard and control a service instantiation."""

    def __init__(self, **kwargs):
        """Initialize ClosedLoop object."""
        self.name = "Custom_controller"
        super().__init__()
        if "service_name" in kwargs:
            self.service_name = kwargs['service_name']
        else:
            raise ValueError("Service Name to specify")
    
    def create_openstack_image(self):
        image = "image with ves agent"
        return image

    def create_service_from_image(self, image):
        service = Service(name=self.service_name)
        #vf vreated from image
        service.add_resource(vf)
        return service
    
    def create_policie(self):
        #create scale out for drools then
        #crete config and policies
        operational_policies = []
        return operational_policies
        return self.instantiate(loop_template=self.check(operational_policies),
                                loop_name=self.name,
                                operational_policies=operational_policies)
    
    def check_deployment(self, action: str):
        done = False
        if action == "create":
            #Check utiliser openstacksdk de python pour vérifier que les 2 VMs sont bien créés
            #wait 5 minustes and check the second
            done = True
        if action == "delete":
            #Check utiliser openstacksdk de python pour vérifier que les 2 VMs sont bien créés
            #wait 5 minustes and check the second
            done = True
        return done

    def e2e(self, delete=True):
        """Closed Loop e2e steps."""
        operational_policies = self.create_policie()
        loop_template = self.check(operational_policies)
        loop_instance = self.instantiate(loop_template=loop_template,
                                         loop_name=self.name,
                                         operational_policies=operational_policies)
        created = self.check_deployment(action="create")
        if not created:
            raise ValueError("Image not created in openstack")
        if delete:
            loop_instance.delete()
            deleted = self.check_deployment(action="delete")
            if not deleted:
                raise ValueError("Image not deleted from openstack")
