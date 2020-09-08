from .settings import * # pylint: disable=W0614e

""" Specific ubuntu16 with multicloud and yaml config scenario."""

USE_MULTICLOUD = True

VENDOR_NAME = "sdktests_vendor"
VSP_NAME = "sdktests_vsp"
VSP_FILE_PATH = "vfw.zip"
SERVICE_NAME = "sdktests-service"
VF_NAME = "sdktests_vf"

CLOUD_REGION_CLOUD_OWNER = "sdktests_cloud_region_owner"
CLOUD_REGION_ID = "sdktests_cloud_region_id"
CLOUD_REGION_TYPE = "openstack"
CLOUD_REGION_VERSION = "titanium_cloud"
CLOUD_DOMAIN = "Default"

COMPLEX_PHYSICAL_LOCATION_ID = "sdktests_complex_physical_location_id"
COMPLEX_DATA_CENTER_CODE = "sdktests_complex_data_center_code"

GLOBAL_CUSTOMER_ID = "sdktests_global_customer_id"
TENANT_ID = ""  # Fill me in your custom settings

VIM_USERNAME = ""  # Fill me in your custom settings
VIM_PASSWORD = ""  # Fill me in your custom settings
VIM_SERVICE_URL = ""  # Fill me in your custom settings

OWNING_ENTITY = "sdktests_owning_entity"
PROJECT = "sdktests_project"
LINE_OF_BUSINESS = "sdktests_line_of_business"
PLATFORM = "sdktests_platform"

SERVICE_INSTANCE_NAME = "sdktests_service_instance_name"

SERVICE_YAML_TEMPLATE = "templates/vnf-services/ubuntu16test-service.yaml"
