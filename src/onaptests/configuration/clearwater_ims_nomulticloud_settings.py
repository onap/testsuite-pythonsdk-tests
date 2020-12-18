import os
import sys
import openstack
from yaml import load

from .global_settings import * # pylint: disable=W0614

""" Specific clearwater IMS without multicloud."""

# pylint: disable=bad-whitespace
# The ONAP part
USE_MULTICLOUD = False
# Set ONLY_INSTANTIATE to true to run an instantiation without repeating
# onboarding and related AAI configuration (Cloud config)
ONLY_INSTANTIATE= False
CLEANUP_FLAG = True
CLEANUP_ACTIVITY_TIMER = 60  # nb of seconds before cleanup in case cleanup option is set
VENDOR_NAME = "clearwater-ims_vendor"

VF_NAME = "clearwater-ims_ubuntu_vf"
VSP_NAME = "clearwater-ims_ubuntu_vsp"
# if a yaml file is define, retrieve info from this yaml files
# if not declare the parameters in the settings
SERVICE_YAML_TEMPLATE = (sys.path[-1] + "/onaptests/templates/vnf-services/" +
                         "clearwater-ims-service.yaml")

try:
    # Try to retrieve the SERVICE NAME from the yaml file
    with open(SERVICE_YAML_TEMPLATE, "r") as yaml_template:
        yaml_config_file = load(yaml_template)
        SERVICE_NAME = next(iter(yaml_config_file.keys()))
except ValueError:
    SERVICE_NAME = "" # Fill me

CLOUD_REGION_CLOUD_OWNER = "clearwater-ims-cloud-owner"
CLOUD_REGION_TYPE = "openstack"
CLOUD_REGION_VERSION = "openstack"

AVAILABILITY_ZONE_NAME = "clearwater-ims-availability-zone"
AVAILABILITY_ZONE_TYPE = "nova"
COMPLEX_PHYSICAL_LOCATION_ID = "lannion"
COMPLEX_DATA_CENTER_CODE = "1234-5"

GLOBAL_CUSTOMER_ID = "clearwater-ims-customer"

OWNING_ENTITY = "clearwater-ims-oe"
PROJECT = "clearwater-ims-project"
LINE_OF_BUSINESS = "clearwater-ims-lob"
PLATFORM = "clearwater-ims-platform"

SERVICE_INSTANCE_NAME = "clearwater-ims_service_instance"

# The cloud Part
# Assuming a cloud.yaml is available, use the openstack client
# to retrieve cloud info and avoid data duplication
TEST_CLOUD = os.getenv('OS_TEST_CLOUD')
cloud = openstack.connect(cloud=TEST_CLOUD)
VIM_USERNAME = cloud.config.auth.get('username','Fill me')
VIM_PASSWORD = cloud.config.auth.get('password','Fill me')
VIM_SERVICE_URL = cloud.config.auth.get('auth_url','Fill me')
TENANT_ID = cloud.config.auth.get('project_id','Fill me')
TENANT_NAME = cloud.config.auth.get('project_name','Fill me')
CLOUD_REGION_ID = cloud.config.get('region_name','RegionOne')
CLOUD_DOMAIN = cloud.config.auth.get('project_domain_name','Default')
