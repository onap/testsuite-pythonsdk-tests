from onaptests.utils.resources import get_resource_location
from .settings import * # pylint: disable=W0614

""" Specific Basic VM with multicloud and yaml config scenario."""
SERVICE_DETAILS = ("Onboarding, distribution and instantiation of a VM" +
                   "using à la carte and Multicloud module")
SERVICE_COMPONENTS="SDC, DMAAP, AAI, SO, SDNC, Multicloud"

USE_MULTICLOUD = True
# Set ONLY_INSTANTIATE to true to run an instantiation without repeating
# onboarding and related AAI configuration (Cloud config)
ONLY_INSTANTIATE= False
VENDOR_NAME = "sdktests_vendor"
SERVICE_NAME = "basicvmtest" # must be the same as in YAML

CLOUD_REGION_CLOUD_OWNER = "sdktestsOwner" # must not contain _
CLOUD_REGION_ID = "RegionOne" # should be valid, as otherwise MultiCloud fails
CLOUD_REGION_TYPE = "openstack"
CLOUD_OWNER_DEFINED_TYPE = "N/A"
CLOUD_REGION_VERSION = "titanium_cloud"
CLOUD_DOMAIN = "Default"

COMPLEX_PHYSICAL_LOCATION_ID = "sdktests_complex_physical_location_id"
COMPLEX_DATA_CENTER_CODE = "sdktests_complex_data_center_code"

GLOBAL_CUSTOMER_ID = "sdktests_global_customer_id"
TENANT_ID = ""  # Fill me in your custom settings
TENANT_NAME= "" # Fill me in your custom settings
AVAILABILITY_ZONE_NAME = "" # Fill me in your custom settings
AVAILABILITY_ZONE_TYPE = "nova"

VIM_USERNAME = ""  # Fill me in your custom settings
VIM_PASSWORD = ""  # Fill me in your custom settings
VIM_SERVICE_URL = ""  # Fill me in your custom settings

OWNING_ENTITY = "sdktests_owning_entity"
PROJECT = "sdktests_project"
LINE_OF_BUSINESS = "sdktests_line_of_business"
PLATFORM = "sdktests_platform"

SERVICE_INSTANCE_NAME = "sdktests_service_instance_name"

SERVICE_YAML_TEMPLATE = get_resource_location("templates/vnf-services/basic_vm-service.yaml")
MODEL_YAML_TEMPLATE = None
