#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
#  pylint: disable=missing-docstring
#  pylint: disable=too-many-branches
#  pylint: disable=too-many-statements
#  pylint: disable=too-many-instance-attributes
#  pylint: disable=invalid-name
"""Onboard class."""
import copy
import os

from onapsdk.sdc.service import Service
from onapsdk.sdc.vendor import Vendor
from onapsdk.sdc.vf import Vf
from onapsdk.sdc.vsp import Vsp
from onapsdk.configuration import settings

from onaptests.actions.common import Common

# PROXY = onap_utils.get_config("general.proxy")


class Onboard(Common):
    """Onboard class to perform SDC operations."""

    def __init__(self, **kwargs):
        """Initialize Onboard object."""
        super().__init__()
        if "service_name" in kwargs:
            self.service_name = kwargs['service_name']
            self.vsp_name = self.service_name + "VSP"
            self.vf_name = self.service_name + "_VF"
            self.vsp_list = []
            self.vf_list = []
        else:
            raise ValueError("Service Name to define")

    def onboard_vsp(self, vendor):
        """Onboard VSP."""
        service_params = self.get_service_custom_config(self.service_name)
        if "vnfs" in service_params:
            for vnf in service_params['vnfs']:
                local_path = os.path.dirname(os.path.abspath(__file__))
                vsp_filepath = local_path.replace("src/onaptests/actions",
                                                  "templates/heat_files/" +
                                                  vnf['heat_files_to_upload'])
                vsp = Vsp(name=vnf['vnf_name'] + "VSP",
                          vendor=vendor,
                          package=open(vsp_filepath, "rb"))
                vsp.onboard()
                self.vsp_list.append(copy.copy(vsp))

    def onboard_vf(self):
        """Onboard VF."""
        service_params = self.get_service_custom_config(
            self.service_name)
        if "vnfs" in service_params:
            for idx, vnf in enumerate(service_params['vnfs']):
                vf = Vf(name=vnf['vnf_name'] + "_VF", vsp=self.vsp_list[idx])
                vf.onboard()
                self.vf_list.append(copy.copy(vf))

    def onboard_resources(self):
        # Onboarding Create SDC resources
        vendor = Vendor(name=settings.VENDOR_NAME)
        vendor.onboard()
        self.onboard_vsp(vendor)
        self.onboard_vf()
        service = Service(name=self.service_name, resources=self.vf_list)
        service.onboard()
        return service
