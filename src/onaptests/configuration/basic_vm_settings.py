import os

import openstack
from yaml import SafeLoader, load

import onaptests.utils.exceptions as onap_test_exceptions
from onaptests.utils.resources import get_resource_location

from .settings import *  # noqa
from .settings import IF_VALIDATION

# The ONAP part
SERVICE_DETAILS = "Onboarding, distribution and instanitation of an Ubuntu VM using à la carte"

USE_MULTICLOUD = False
# Set ONLY_INSTANTIATE to true to run an instantiation without repeating
# onboarding and related AAI configuration (Cloud config)
ONLY_INSTANTIATE = False

# if a yaml file is define, retrieve info from this yaml files
# if not declare the parameters in the settings
SERVICE_YAML_TEMPLATE = get_resource_location("templates/vnf-services/basic_vm-service.yaml")
generate_service_config_yaml_file(service_name="basic_vm",  # noqa
                                  service_template="basic_vm-service.yaml.j2",
                                  service_config=SERVICE_YAML_TEMPLATE)

try:
    # Try to retrieve the SERVICE NAME from the yaml file
    with open(SERVICE_YAML_TEMPLATE, "r", encoding="utf-8") as yaml_template:
        yaml_config_file = load(yaml_template, SafeLoader)
        SERVICE_NAME = next(iter(yaml_config_file.keys()))
except (FileNotFoundError, ValueError) as exc:
    raise onap_test_exceptions.TestConfigurationException from exc

CLEANUP_FLAG = True
CLEANUP_ACTIVITY_TIMER = 10  # nb of seconds before cleanup in case cleanup option is set
VENDOR_NAME = "basicvm_vendor"

VF_NAME = "basicvm_ubuntu_vf"
VSP_NAME = "basicvm_ubuntu_vsp"

CLOUD_REGION_CLOUD_OWNER = "basicvm-cloud-owner"
CLOUD_REGION_TYPE = "openstack"
CLOUD_REGION_VERSION = "openstack"
CLOUD_OWNER_DEFINED_TYPE = "N/A"

AVAILABILITY_ZONE_NAME = "basicvm-availability-zone"
AVAILABILITY_ZONE_TYPE = "nova"
COMPLEX_PHYSICAL_LOCATION_ID = "lannion"
COMPLEX_DATA_CENTER_CODE = "1234-5"

GLOBAL_CUSTOMER_ID = "basicvm-customer"

OWNING_ENTITY = "basicvm-oe"
PROJECT = "basicvm-project"
LINE_OF_BUSINESS = "basicvm-lob"
PLATFORM = "basicvm-platform"

SERVICE_INSTANCE_NAME = "basic_vm_service_instance"

# The cloud Part
# Assuming a cloud.yaml is available, use the openstack client
# to retrieve cloud info and avoid data duplication
if not IF_VALIDATION:
    TEST_CLOUD = os.getenv('OS_TEST_CLOUD')
    cloud = openstack.connect(cloud=TEST_CLOUD)
    VIM_USERNAME = cloud.config.auth.get('username', 'Fill me')
    VIM_PASSWORD = cloud.config.auth.get('password', 'Fill me')
    VIM_SERVICE_URL = cloud.config.auth.get('auth_url', 'Fill me')
    TENANT_ID = cloud.config.auth.get('project_id', 'Fill me')
    TENANT_NAME = cloud.config.auth.get('project_name', 'Fill me')
    CLOUD_REGION_ID = cloud.config.auth.get('region_name', 'RegionOne')
    CLOUD_DOMAIN = cloud.config.auth.get('project_domain_name', 'Default')

MODEL_YAML_TEMPLATE = None
