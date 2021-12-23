import os
import openstack
from pathlib import Path
from uuid import uuid4
from yaml import load, SafeLoader

import onaptests.utils.exceptions as onap_test_exceptions
from onaptests.utils.resources import get_resource_location
from .settings import * # pylint: disable=W0614


CLEANUP_FLAG = True

CDS_DD_FILE = Path(get_resource_location("templates/artifacts/dd.json"))
CDS_CBA_UNENRICHED = Path(get_resource_location("templates/artifacts/basic_vm_cba.zip"))
CDS_CBA_ENRICHED = "/tmp/BASIC_VM_enriched.zip"

ONLY_INSTANTIATE = False
USE_MULTICLOUD = False

VENDOR_NAME = "basicvm_macro_vendor"

CLOUD_REGION_CLOUD_OWNER = "basicvm-macro-cloud-owner"
CLOUD_REGION_TYPE = "openstack"
CLOUD_REGION_VERSION = "pike"
CLOUD_OWNER_DEFINED_TYPE = "N/A"

AVAILABILITY_ZONE_NAME = "basicvm-macro-availability-zone"
AVAILABILITY_ZONE_TYPE = "nova"
COMPLEX_PHYSICAL_LOCATION_ID = "lannion"
COMPLEX_DATA_CENTER_CODE = "1234-5"

GLOBAL_CUSTOMER_ID = "basicvm-customer"

TEST_CLOUD = os.getenv('OS_TEST_CLOUD')
cloud = openstack.connect(cloud=TEST_CLOUD)
VIM_USERNAME = cloud.config.auth.get('username','Fill me')
VIM_PASSWORD = cloud.config.auth.get('password','Fill me')
VIM_SERVICE_URL = cloud.config.auth.get('auth_url','Fill me')
TENANT_ID = cloud.config.auth.get('project_id','Fill me')
TENANT_NAME = cloud.config.auth.get('project_name','Fill me')
CLOUD_REGION_ID = cloud.config.auth.get('region_name','RegionOne')
CLOUD_DOMAIN = cloud.config.auth.get('project_domain_name','Default')

OWNING_ENTITY = "basicvm-oe"
PROJECT = "basicvm-project"
LINE_OF_BUSINESS = "basicvm-lob"
PLATFORM = "basicvm-platform"
CLOUD_DOMAIN = "Default"
SERVICE_YAML_TEMPLATE = Path(get_resource_location("templates/vnf-services/basic_vm_macro-service.yaml"))

try:
    # Try to retrieve the SERVICE NAME from the yaml file
    with open(SERVICE_YAML_TEMPLATE, "r") as yaml_template:
        yaml_config_file = load(yaml_template, SafeLoader)
        SERVICE_NAME = next(iter(yaml_config_file.keys()))
except (FileNotFoundError, ValueError):
    raise onap_test_exceptions.TestConfigurationException

SERVICE_INSTANCE_NAME = f"basic_macro_{str(uuid4())}"

MODEL_YAML_TEMPLATE = None
