#!/usr/bin/python
# http://www.apache.org/licenses/LICENSE-2.0
"""Clamp Onboard service class."""
from onapsdk.sdc.vendor import Vendor
from onapsdk.sdc.service import Service

from onaptests.configuration import settings
from onaptests.actions.onboard import Onboard


class OnboardClamp(Onboard):
    """Onboard class to create CLAMP templates."""

    def __init__(self, **kwargs):
        """Initialize Onboard object."""
        if "service_name" in kwargs:
            self.service_name = kwargs['service_name']
        else:
            raise ValueError("Service Name to define")
        self.vf_list = []
        self.vsp_list = []
    
    def onboard_artifact(self):
        """Create service with artifact from scratch."""
        vendor = Vendor(name=settings.VENDOR_NAME)
        vendor.onboard()
        self.onboard_vsp(vendor)
        # only 1 vf to onboard
        self.onboard_vf()
        service = Service(name=self.service_name)
        service.create()
        for vf in self.vf_list:
            service.add_resource(vf)
        vnf = service.vnfs[0].name
        payload_file = open(settings.CONFIGURATION_PATH + '/clampnode.yaml', 'rb')
        data = payload_file.read()
        service.add_artifact_to_vf(vnf_name=vnf,
                                   artifact_type="DCAE_INVENTORY_BLUEPRINT",
                                   artifact_name="clampnode.yaml",
                                   artifact=data)
        payload_file.close()
        service.checkin()
        service.onboard()
        return service
