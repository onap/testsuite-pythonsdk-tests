#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
"""E2E closed loop class."""
import time
import openstack

from onapsdk.clamp.clamp_element import Clamp
from onapsdk.clamp.loop_instance import LoopInstance
from onapsdk.sdc.service import Service

from onaptests.configuration import settings
from onaptests.clamp_scenario import ClampScenario
from onaptests.scenario import Scenario
from onaptests.actions.instantiate_loop import InstantiateLoop


class ClosedLoop(ClampScenario, Scenario):
    """Closed Loop class to onboard and control a service instantiation."""

    def __init__(self, **kwargs):
        """Initialize ClosedLoop object."""
        self.name = "Custom_controller"
        if "service_name" in kwargs:
            self.service_name = kwargs['service_name']
        else:
            raise ValueError("Service Name to specify")
        Service.set_proxy({ 'http': settings.SOCK_HTTP, 'https': settings.SOCK_HTTP})
        Clamp.set_proxy({ 'http': settings.SOCK_HTTP, 'https': settings.SOCK_HTTP})
        # must change cert path in python-onapsdk configuration
        Clamp.create_cert()
        openstack.enable_logging(debug=True)
        self.image_creation = 300
        self.image = 'test-closed-loop'

    def create_openstack_image(self, conn):
        """Get openstack ubuntu image."""
        image = conn.image.find_image("ubuntu-18.04-daily")
        response = conn.image.download_image(image)
        #data = add_VES_agent(response) # an outer function
        image_attrs = {
            'name': self.image,
            'data': data,
            'disk_format': 'raw',
            'container_format': 'bare',
            'visibility': 'public',
        }
        conn.image.upload_image(**image_attrs)
        return image

    def create_service_from_image(self, conn):
        """Create service from an openstack image that contains VES Agent."""
        image = self.create_openstack_image(conn)
        # create vnf from image
        # self.onboard()
        # return service

    def create_policies(self):
        """Create the desired policies with customized config."""
        operational_policies = []
        #create scale out for drools then
        #create policies and configure them
        return operational_policies

    def check_deployment(self, conn, action: str):
        """Check in openstack if the action was correctly done."""
        done = False
        images = []
        images = conn.image.images()
        if action == "create":
            first_vm = (len(images) == 1)
            time.sleep(self.image_creation)
            done = (len(images) == 2 and first_vm)
        if action == "delete":
            done = (len(images) == 0)
        return done

    def e2e(self, delete=True):
        """Closed Loop e2e steps."""
        conn = openstack.connect(cloud=settings.TENANT_USER_NAME)

        service = self.create_service_from_image(conn)
        operational_policies = self.create_policies()
        loop_template = self.check(operational_policies)
        loop_instance = self.instantiate_clamp(loop_template=loop_template,
                                               loop_name=self.name,
                                               operational_policies=operational_policies)
        # deploy service
        instance_name = self.service_name + "-" + str(uuid4())
        service_instance = self.instantiate(instance_name, cloud, service)
        # end
        created = self.check_deployment(conn, action="create")
        if not created:
            raise ValueError("Image not created in openstack")
        if delete:
            loop_instance.delete()
            # delete service
            self.clean(self.service_name,
                       service_instance=service_instance)
            # end
            deleted = self.check_deployment(conn, action="delete")
            if not deleted:
                raise ValueError("Image not deleted from openstack")
            image = conn.image.find_image(self.image)
            conn.image.delete_image(image, ignore_missing=False)
