import os
import openstack

# pylint: disable=unused-import
from .settings import *

# The ONAP part
USE_MULTICLOUD = False

VENDOR_NAME = "basicvm_vendor"
VSP_NAME = "basicvm_ubuntu_vsp"
SERVICE_NAME = "basicvm-ubuntu-service"
VF_NAME = "basicvm_ubuntu_vf"

CLOUD_REGION_CLOUD_OWNER = "basicvm-cloud-owner"
CLOUD_REGION_ID = "RegionOne"
CLOUD_REGION_TYPE = "openstack"
CLOUD_REGION_VERSION = "openstack"
CLOUD_DOMAIN = "Default"

AVAILABILITY_ZONE_NAME = "basicvm-availability-zone"
AVAILABILITY_ZONE_TYPE = "nova"
COMPLEX_PHYSICAL_LOCATION_ID = "lannion"
COMPLEX_DATA_CENTER_CODE = "1234-5"

GLOBAL_CUSTOMER_ID = "basicvm-customer"

OWNING_ENTITY = "basicvm-oe"
PROJECT = "basicvm-project"
LINE_OF_BUSINESS = "basicvm-lob"
PLATFORM = "basicvm-platform"

SERVICE_INSTANCE_NAME = "basicvm_ubuntu16_service_instance"

VSP_FILE_PATH = "templates/heat_files/ubuntu16/ubuntu16.zip"

# The cloud Part
# TODO use the openstack client and assume a cloud.yaml is Provided
# to avoid data duplication
CLOUD_REGION_ID = "RegionOne"

TEST_CLOUD = os.getenv('OS_TEST_CLOUD', 'onap-cloud-config')
try:
    cloud = openstack.connect(cloud=TEST_CLOUD)
    VIM_USERNAME = cloud.config.auth['username']
    VIM_PASSWORD = cloud.config.auth['password']
    VIM_SERVICE_URL = cloud.config.auth['auth_url']
    # need a keystone authent to retrieve project info
    TENANT_ID = "" # Fill me
    TENANT_NAME = "" # Fill me
except ValueError:
    TENANT_ID = "" # Fill me
    TENANT_NAME = "" # Fill me
    VIM_USERNAME = ""  # Fill me
    VIM_PASSWORD = ""  # Fill me
    VIM_SERVICE_URL = ""  # Fill me
