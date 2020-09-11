from .settings import * # pylint: disable=W0614

""" Specific ubuntu16 with multicloud and yaml config scenario."""

USE_MULTICLOUD = True

VENDOR_NAME = "sdktests_vendor"
SERVICE_NAME = "basic_network" # must be the same as in YAML

CLOUD_REGION_CLOUD_OWNER = "CloudOwner" # Restiction in SDNC (SDNC-1260)
CLOUD_REGION_ID = "RegionOne"
CLOUD_REGION_TYPE = "openstack"
CLOUD_REGION_VERSION = "titanium_cloud"
CLOUD_DOMAIN = "Default"

COMPLEX_PHYSICAL_LOCATION_ID = "sdktests_complex_physical_location_id"
COMPLEX_DATA_CENTER_CODE = "1234"

GLOBAL_CUSTOMER_ID = "sdktests_global_customer_id"
TENANT_ID = ""  # Fill me in your custom settings
TENANT_NAME= ""  # Fill me in your custom settings
AVAILABILITY_ZONE_NAME = "nova"
AVAILABILITY_ZONE_TYPE = "nova"

VIM_USERNAME = ""  # Fill me in your custom settings
VIM_PASSWORD = ""  # Fill me in your custom settings
VIM_SERVICE_URL = ""  # Fill me in your custom settings

OWNING_ENTITY = "sdktests_owning_entity"
PROJECT = "sdktests_project"
LINE_OF_BUSINESS = "sdktests_line_of_business"
PLATFORM = "sdktests_platform"

SERVICE_INSTANCE_NAME = "sdktests_network-1"

SERVICE_YAML_TEMPLATE = "templates/vnf-services/basic_network-service.yaml"
