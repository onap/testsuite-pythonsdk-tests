import os

from yaml import SafeLoader, load

import onaptests.utils.exceptions as onap_test_exceptions
from onaptests.utils.resources import get_resource_location

from .settings import *  # noqa

# Specific basic_cnf with multicloud-k8s and yaml config scenario.
SERVICE_DETAILS = ("Onboarding, distribution and instantiation of a CNF" +
                   "using à la carte and Multicloud K8S module")
# This scenario uses multicloud-k8s and not multicloud
# (no registration requested)
USE_MULTICLOUD = False
# Set ONLY_INSTANTIATE to true to run an instantiation without repeating
# onboarding and related AAI configuration (Cloud config)
ONLY_INSTANTIATE = False

# if a yaml file is define, retrieve info from this yaml files
# if not declare the parameters in the settings
SERVICE_YAML_TEMPLATE = get_resource_location("templates/vnf-services/basic_cnf-service.yaml")

try:
    # Try to retrieve the SERVICE NAME from the yaml file
    with open(SERVICE_YAML_TEMPLATE, "r", encoding="utf-8") as yaml_template:
        yaml_config_file = load(yaml_template, SafeLoader)
        SERVICE_NAME = next(iter(yaml_config_file.keys()))
except (FileNotFoundError, ValueError) as exc:
    raise onap_test_exceptions.TestConfigurationException from exc

CLEANUP_FLAG = True
# nb of seconds before cleanup in case cleanup option is set
CLEANUP_ACTIVITY_TIMER = 10

# Definition of k8s profile version
K8S_PROFILE_K8S_VERSION = "1.0"
# Relative path to k8s profile artifact in the python package (so under /src)
K8S_PROFILE_ARTIFACT_PATH = get_resource_location("templates/artifacts/k8sprof.tar.gz")
# Relative path to config file to set k8s connectivity information
K8S_CONFIG = get_resource_location("templates/artifacts/config")

VENDOR_NAME = "basicnf_vendor"

CLOUD_REGION_CLOUD_OWNER = "basicnf-owner"  # must not contain _
CLOUD_REGION_ID = "k8sregion"
CLOUD_REGION_TYPE = "k8s"
CLOUD_REGION_VERSION = "1.0"
CLOUD_DOMAIN = "Default"
CLOUD_OWNER_DEFINED_TYPE = "t1"

COMPLEX_PHYSICAL_LOCATION_ID = "lannion"
COMPLEX_DATA_CENTER_CODE = "1234-5"
AVAILABILITY_ZONE_NAME = "basicnf-availability-zone"
AVAILABILITY_ZONE_TYPE = "nova"

GLOBAL_CUSTOMER_ID = "basicnf-customer"

OWNING_ENTITY = "basicnf_owning_entity"
PROJECT = "basicnf_project"
LINE_OF_BUSINESS = "basicnf_lob"
PLATFORM = "basicnf_platform"

SERVICE_INSTANCE_NAME = "basic_cnf_service_instance"

# The cloud Part
# Assuming a cloud.yaml is available, use the openstack client
# to retrieve cloud info and avoid data duplication
# For basic_cnf, no tenant information is required but some dummy
# information shall be provided by default
# So it is not requested to set OS_TEST_CLOUD
TEST_CLOUD = os.getenv('OS_TEST_CLOUD')
VIM_USERNAME = 'dummy'
VIM_PASSWORD = 'dummy123'
VIM_SERVICE_URL = 'http://10.12.25.2:5000/v3'
TENANT_ID = '123456'
TENANT_NAME = 'dummy_test'

MODEL_YAML_TEMPLATE = None
