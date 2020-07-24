#!/usr/bin/python
# http://www.apache.org/licenses/LICENSE-2.0
"""Clamp Onboard service class."""
import os

from onapsdk.sdc.vendor import Vendor
from onapsdk.sdc.service import Service

from onaptests.actions.onboard import Onboard


class OnboardClamp(Onboard):
    """Onboard class to create CLAMP templates."""

    def __init__(self, **kwargs):
        """Initialize Onboard object."""
        super().__init__()
        if "service_name" in kwargs:
            self.service_name = kwargs['service_name']
            self.vnf_name = "test 0"#self.service_name + '_VF'
        else:
            raise ValueError("Service Name to define")
    
    def onboard_artifact(self):
        """Create service with artifact from scratch."""
        vendor = Vendor(name='generic')
        vendor.onboard()
        self.onboard_vsp(vendor)
        # only 1 vf to onboard
        self.onboard_vf()
        service = Service(name=self.service_name, resources=self.vf_list)
        local_path = os.path.dirname(os.path.abspath(__file__))
        payload_file = open("{}/clampnode.yaml".format(local_path), 'rb')
        data = payload_file.read()
        svc.add_artifact_to_vf(vnf_name=self.vf_list[0].name,
                               artifact_type="DCAE_INVENTORY_BLUEPRINT", #for clamp purposes
                               artifact_name="clampnode.yaml",
                               artifact=data)
        payload_file.close()
        service.onboard()
        return service
