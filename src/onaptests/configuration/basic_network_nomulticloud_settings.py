import os
import openstack
import sys
from yaml import load

import onaptests.utils.exceptions as onap_test_exceptions
from .settings import * # pylint: disable=W0614

""" Specific Basic Network without multicloud."""

# pylint: disable=bad-whitespace
# The ONAP part
SERVICE_DETAILS="Onboarding, distribution and instantiation of Basic Network using à la carte"
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
except (FileNotFoundError, ValueError):
    raise onap_test_exceptions.TestConfigurationException

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
TEST_CLOUD = os.getenv('OS_TEST_CLOUD')
cloud = openstack.connect(cloud=TEST_CLOUD)
VIM_USERNAME = cloud.config.auth.get('username','Fill me')
VIM_PASSWORD = cloud.config.auth.get('password','Fill me')
VIM_SERVICE_URL = cloud.config.auth.get('auth_url','Fill me')
TENANT_ID = cloud.config.auth.get('project_id','Fill me')
TENANT_NAME = cloud.config.auth.get('project_name','Fill me')
CLOUD_REGION_ID = cloud.config.auth.get('region_name','RegionOne')
CLOUD_DOMAIN = cloud.config.auth.get('project_domain_name','Default')
