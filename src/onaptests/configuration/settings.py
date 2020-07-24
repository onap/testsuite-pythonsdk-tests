"""Specific settings module."""  # pylint: disable=bad-whitespace
import os
######################
#                    #
# ONAP INPUTS DATAS  #
#                    #
######################

# Define cloud infrastructure
GLOBAL_CUSTOMER_ID = "generic"
VENDOR_NAME = "generic"

COMPLEX_PHYSICAL_LOCATION_ID = "cruguil"
COMPLEX_DATA_CENTER_CODE = "22300"

CLOUD_REGION_ID = "RegionOne"
CLOUD_REGION_OWNER = "test"
TENANT_ID = "cdc59e3371e34368839e7051e325f614"
TENANT_NAME = "onap-master-daily-vnfs"
TENANT_USER_NAME = "onap-master-daily-vnfs-ci"
TENANT_USER_PWD = "sZb4hytF7iPSSiq2F3HhoUYkIhSXGAmH"
TENANT_KEYSTONE_URL = "https://vim.pod4.opnfv.fr:5000/v3"

SOCK_HTTP = "socks5h://127.0.0.1:8080"

# PATHS
TEMPLATES_PATH = os.getcwd().rsplit('/onaptests')[0]+"/templates"
CONFIGURATION_PATH = os.getcwd().rsplit('/onaptests')[0]+"/src/onaptests/configuration"
