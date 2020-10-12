import os
import openstack
import sys
from yaml import load

from .settings import * # pylint: disable=W0614

""" Specific ubuntu16 without multicloud."""

# pylint: disable=bad-whitespace
# The ONAP part
SERVICE_DETAILS="Onboarding, distribution and instanitation of asic Network using à la carte"
SERVICE_COMPONENTS="SDC, DMAAP, AAI, SO, SDNC"
USE_MULTICLOUD = False
# Set ONLY_INSTANTIATE to true to run an instantiation without repeating
# onboarding and related AAI configuration (Cloud config)
ONLY_INSTANTIATE= False

# if a yaml file is define, retrieve info from this yaml files
# if not declare the parameters in the settings
SERVICE_YAML_TEMPLATE = (sys.path[-1] + "/onaptests/templates/vnf-services/" +
                         "basic_network-service.yaml")

try:
    # Try to retrieve the SERVICE NAME from the yaml file
    with open(SERVICE_YAML_TEMPLATE, "r") as yaml_template:
        yaml_config_file = load(yaml_template)
        SERVICE_NAME = next(iter(yaml_config_file.keys()))
except ValueError:
    SERVICE_NAME = "" # Fill me

CLEANUP_FLAG = True
CLEANUP_ACTIVITY_TIMER = 10  # nb of seconds before cleanup in case cleanup option is set
VENDOR_NAME = "basicnw_vendor"

CLOUD_REGION_CLOUD_OWNER = "basicnw-cloud-owner"
CLOUD_REGION_TYPE = "openstack"
CLOUD_REGION_VERSION = "openstack"
CLOUD_OWNER_DEFINED_TYPE = "N/A"

AVAILABILITY_ZONE_NAME = "basicvm-availability-zone"
AVAILABILITY_ZONE_TYPE = "nova"
COMPLEX_PHYSICAL_LOCATION_ID = "lannion"
COMPLEX_DATA_CENTER_CODE = "1234-5"

GLOBAL_CUSTOMER_ID = "basicnw-customer"

OWNING_ENTITY = "basicnw-oe"
PROJECT = "basicnw-project"
LINE_OF_BUSINESS = "basicnw-lob"
PLATFORM = "basicnw-platform"

SERVICE_INSTANCE_NAME = "basicnw_service_instance"

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
