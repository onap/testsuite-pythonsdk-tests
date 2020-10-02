import os
import openstack
import sys
from yaml import load

from .settings import * # pylint: disable=W0614

""" Specific basic_cnf with multicloud-k8s and yaml config scenario."""

# This scenario uses multicloud-k8s and not multicloud
# (no registration requested)
USE_MULTICLOUD = False
# Set ONLY_INSTANTIATE to true to run an instantiation without repeating
# onboarding and related AAI configuration (Cloud config)
ONLY_INSTANTIATE= False

# if a yaml file is define, retrieve info from this yaml files
# if not declare the parameters in the settings
SERVICE_YAML_TEMPLATE = (sys.path[-1] + "/onaptests/templates/vnf-services/" +
                         "basic_cnf-service.yaml")

try:
    # Try to retrieve the SERVICE NAME from the yaml file
    with open(SERVICE_YAML_TEMPLATE, "r") as yaml_template:
        yaml_config_file = load(yaml_template)
        SERVICE_NAME = next(iter(yaml_config_file.keys()))
except ValueError:
    SERVICE_NAME = "" # Fill me

CLEANUP_FLAG = True
# nb of seconds before cleanup in case cleanup option is set
CLEANUP_ACTIVITY_TIMER = 10

# Definition of k8s profile
K8S_PROFILE_NAME = "cnftest"
K8S_PROFILE_NAMESPACE = "k8s"
K8S_PROFILE_K8S_VERSION = "1.0"
# Relative path to k8s profile artifact in the python package (so under /src)
K8S_PROFILE_ARTIFACT_PATH = (sys.path[-1] +
                             "/onaptests/templates/artifacts/k8sprof.tar.gz")
# Relative path to config file to set k8s connectivity information
K8S_KUBECONFIG_FILE = (sys.path[-1] +
                       "/onaptests/templates/artifacts/config")

VENDOR_NAME = "basicnf_vendor"

CLOUD_REGION_CLOUD_OWNER = "basicnf-owner" # must not contain _
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
TEST_CLOUD = os.getenv('OS_TEST_CLOUD')
try:
    if TEST_CLOUD is not None:
        cloud = openstack.connect(cloud=TEST_CLOUD)
        VIM_USERNAME = cloud.config.auth['username']
        VIM_PASSWORD = cloud.config.auth['password']
        VIM_SERVICE_URL = cloud.config.auth['auth_url']
        TENANT_ID = cloud.config.auth['project_id']
        TENANT_NAME = cloud.config.auth['project_name']
    else:
        raise KeyError
except KeyError:
    # If you do not use the cloud.yaml as imput for your openstack
    # put the input data here
    # Note if 1 parameter is missing in the clouds.yaml, we fallback here
    "Dummy definition - not used"
    TENANT_ID = "123456"
    TENANT_NAME = "dummy_test"
    VIM_USERNAME = "dummy"
    VIM_PASSWORD = "dummy123"
    VIM_SERVICE_URL = "http://10.12.25.2:5000/v3"  # Fill me
