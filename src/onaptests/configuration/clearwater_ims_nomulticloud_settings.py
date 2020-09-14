import os
import openstack
from yaml import load

from .settings import * # pylint: disable=W0614

""" Specific clearwater IMS without multicloud."""

# pylint: disable=bad-whitespace
# The ONAP part
USE_MULTICLOUD = False
SERVICE_YAML_TEMPLATE = "templates/vnf-services/clearwater-ims-service.yaml"
CLEANUP_FLAG = True
CLEANUP_ACTIVITY_TIMER = 60  # nb of seconds before cleanup in case cleanup option is set
VENDOR_NAME = "clearwater-ims_vendor"

VF_NAME = "clearwater-ims_ubuntu_vf"
VSP_NAME = "clearwater-ims_ubuntu_vsp"
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

SERVICE_INSTANCE_NAME = "clearwater-ims_service_instance_7"

VSP_FILE_PATH = "templates/heat_files/clearwater_ims/clearwater_ims.zip"


# The cloud Part
# Assuming a cloud.yaml is available, use the openstack client
# to retrieve cloud info and avoid data duplication
TEST_CLOUD = os.getenv('OS_TEST_CLOUD')
try:
    if TEST_CLOUD is not None:
        cloud = openstack.connect(cloud=TEST_CLOUD)
        VIM_USERNAME = cloud.config.auth['username']
        VIM_PASSWORD = cloud.config.auth['password']
        VIM_SERVICE_URL = cloud.config.auth['auth_url']
        TENANT_ID = cloud.config.auth['project_id']
        TENANT_NAME = cloud.config.auth['project_name']
        CLOUD_REGION_ID = cloud.config.region_name
        CLOUD_DOMAIN = cloud.config.auth['project_domain_name']
    else:
        raise KeyError
except KeyError:
    # If you do not use the cloud.yaml as imput for your openstack
    # put the input data here
    # Note if 1 parameter is missing in the clouds.yaml, we fallback here
    TENANT_ID = "" # Fill me
    TENANT_NAME = "" # Fill me
    VIM_USERNAME = ""  # Fill me
    VIM_PASSWORD = ""  # Fill me
    VIM_SERVICE_URL = ""  # Fill me
    CLOUD_REGION_ID = "RegionOne" # Update me if needed
    CLOUD_DOMAIN = "Default" # Update me if needed
