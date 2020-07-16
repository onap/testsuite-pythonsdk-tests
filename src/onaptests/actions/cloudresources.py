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
from uuid import uuid4
from onapsdk.configuration import settings
from onapsdk.aai.cloud_infrastructure import (
    CloudRegion,
    Complex
)

from onapsdk.aai.business import OwningEntity as AaiOwningEntity

from onapsdk.vid import LineOfBusiness, OwningEntity, Platform, Project

from onaptests.actions.common import Common

class CloudResources(Common):
    """
    Class to create cloud resources in AAI
    """

    def __init__(self):
        """Initialize objects."""
        super().__init__()
        self.cloud_region = None
        self.owning_entity = None
        self.project = None
        self.platform = None
        self.line_of_business = None

    def declare_aai_region(self):
        """Initialize aai region."""
        self.logger.info("*******************************")
        self.logger.info("***** RUNTIME PREPARATION *****")
        self.logger.info("*******************************")

        self.logger.info("*Check if cloud region exists *")
        try:
            cloud_region = CloudRegion.get_by_id(settings.CLOUD_REGION_OWNER,
                                                 settings.CLOUD_REGION_ID)
        except ValueError:
            cloud_region = None
        if not cloud_region:
            self.logger.info("******** Create Complex *******")
            cmplx = Complex.create(
                physical_location_id=settings.COMPLEX_PHYSICAL_LOCATION_ID,
                data_center_code=settings.COMPLEX_DATA_CENTER_CODE,
                name=settings.COMPLEX_PHYSICAL_LOCATION_ID,
            )
            self.logger.info("******** Create CloudRegion *******")
            cloud_region = CloudRegion.create(
                cloud_owner=settings.CLOUD_REGION_OWNER,
                cloud_region_id=settings.CLOUD_REGION_ID,
                orchestration_disabled=False,
                in_maint=False,
                cloud_type="openstack",
                cloud_region_version="na",
            )
            cloud_region.add_availability_zone("nova", "KVM")
            self.logger.info("******** Link Complex to CloudRegion *******")
            cloud_region.link_to_complex(cmplx)

            self.logger.info("******** Add ESR Info to CloudRegion *******")
            cloud_region.add_esr_system_info(
                esr_system_info_id=str(uuid4()),
                user_name=settings.TENANT_USER_NAME,
                password=settings.TENANT_USER_PWD,
                system_type="openstack",
                service_url=settings.TENANT_KEYSTONE_URL,
                cloud_domain="Default",
            )
            self.logger.info("******** Add ESR Info to CloudRegion *******")
            cloud_region.add_tenant(tenant_id=settings.TENANT_ID,
                                    tenant_name=settings.TENANT_NAME)
        return cloud_region

    def declare_owning_entity(self):
        """Declare owning entity if not created."""
        self.logger.info("******** Add Owning Entity in AAI *******")
        vid_owning_entity = OwningEntity.create("OE-Generic")
        owning_entity = None
        for oe_element in AaiOwningEntity.get_all():
            self.logger.debug("OE %s checked", oe_element.name)
            if oe_element.name == vid_owning_entity.name:
                self.logger.debug("OE %s found", oe_element.name)
                owning_entity = oe_element
                break
        if not owning_entity:
            self.logger.info("******** Owning Entity not existing: create *******")
            owning_entity = AaiOwningEntity.create(vid_owning_entity.name, str(uuid4()))
        return owning_entity

    def add_cloud_resources(self):
        """Add Cloud resources."""
        self.logger.info("******** AAI declaration *******")
        self.cloud_region = self.declare_aai_region()
        self.owning_entity = self.declare_owning_entity()
        self.project = Project.create("SDKTest-project")
        self.platform = Platform.create("SDKTest-PLATFORM")
        self.line_of_business = LineOfBusiness.create("SDKTest-BusinessLine")
