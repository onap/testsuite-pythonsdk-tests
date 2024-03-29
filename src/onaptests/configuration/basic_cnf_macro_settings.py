import os
from pathlib import Path
from uuid import uuid4

from yaml import SafeLoader, load

import onaptests.utils.exceptions as onap_test_exceptions
from onaptests.utils.resources import get_resource_location

from .settings import *  # noqa

# Specific basic_cnf_macro with multicloud-k8s and yaml config scenario.
SERVICE_DETAILS = ("Onboarding, distribution and instantiation of a Apache CNF " +
                   "using macro and native CNF path: cnf-adapter + K8sPlugin")

CLEANUP_FLAG = True

# CDS_DD_FILE = Path(get_resource_location("templates/artifacts/dd.json"))
CDS_CBA_UNENRICHED = Path("no_such_file")
CDS_CBA_ENRICHED = Path(get_resource_location("templates/artifacts/basic_cnf_cba_enriched.zip"))

# This scenario uses multicloud-k8s and not multicloud
# (no registration requested)
USE_MULTICLOUD = False
# Set ONLY_INSTANTIATE to true to run an instantiation without repeating
# onboarding and related AAI configuration (Cloud config)
ONLY_INSTANTIATE = False

# Relative path to config file to set k8s connectivity information
K8S_CONFIG = get_resource_location("templates/artifacts/config")

VENDOR_NAME = "basiccnf_macro_vendor"

CLOUD_REGION_CLOUD_OWNER = "basiccnf-cloud-owner"  # must not contain _
CLOUD_REGION_ID = "k8sregion-cnf-macro"
CLOUD_REGION_TYPE = "k8s"
CLOUD_REGION_VERSION = "1.0"
CLOUD_DOMAIN = "Default"
CLOUD_OWNER_DEFINED_TYPE = "t1"

COMPLEX_PHYSICAL_LOCATION_ID = "lannion"
COMPLEX_DATA_CENTER_CODE = "1234-5"
AVAILABILITY_ZONE_NAME = "basiccnf-availability-zone"
AVAILABILITY_ZONE_TYPE = "nova"

GLOBAL_CUSTOMER_ID = "basiccnf-macro-customer"

OWNING_ENTITY = "basicnf_macro_owning_entity"
PROJECT = "basicnf_macro_project"
LINE_OF_BUSINESS = "basicnf_macro_lob"
PLATFORM = "basicnf_macro_platform"

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


SERVICE_YAML_TEMPLATE = Path(get_resource_location(
    "templates/vnf-services/basic_cnf_macro-service.yaml"))
generate_service_config_yaml_file(service_name="basic_cnf_macro",  # noqa
                                  service_template="basic_cnf_macro-service.yaml.j2",
                                  service_config=SERVICE_YAML_TEMPLATE)

try:
    # Try to retrieve the SERVICE NAME from the yaml file
    with open(SERVICE_YAML_TEMPLATE, "r", encoding="utf-8") as yaml_template:
        yaml_config_file = load(yaml_template, SafeLoader)
        SERVICE_NAME = next(iter(yaml_config_file.keys()))
except (FileNotFoundError, ValueError) as exc:
    raise onap_test_exceptions.TestConfigurationException from exc

SERVICE_INSTANCE_NAME = f"basic_cnf_macro_{str(uuid4())}"

MODEL_YAML_TEMPLATE = None
