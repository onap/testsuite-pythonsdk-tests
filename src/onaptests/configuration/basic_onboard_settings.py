import os
import sys
import random
import string
import openstack

from yaml import load

from jinja2 import Environment, PackageLoader
import onaptests.utils.exceptions as onap_test_exceptions
from .settings import * # pylint: disable=W0614

# We need to create a service file with a random service name,
# to be sure that we force onboarding
def generate_service_config_yaml_file():
    """ generate the service file with a random service name
     from a jinja template"""

    env = Environment(
        loader=PackageLoader('onaptests', 'templates/vnf-services'),
    )
    template = env.get_template('basic_onboard-service.yaml.j2')

    # get a random string to randomize the vnf name
    # Random string with the combination of lower and upper case
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(6))
    service_name = 'basic_onboard_' + result_str

    rendered_template = template.render(service_name=service_name)

    file_name = (sys.path[-1] + "/onaptests/templates/vnf-services/" +
                 "basic-onboard-service.yaml")

    with open(file_name, 'w+') as file_to_write:
        file_to_write.write(rendered_template)

"""Basic onboard service to only onboard a service in SDC"""

# pylint: disable=bad-whitespace
# The ONAP part
SERVICE_DETAILS="Onboarding of an Ubuntu VM"
SERVICE_COMPONENTS="SDC"

USE_MULTICLOUD = False
# Set ONLY_INSTANTIATE to true to run an instantiation without repeating
# onboarding and related AAI configuration (Cloud config)
ONLY_INSTANTIATE= False

# if a yaml file is define, retrieve info from this yaml files
# if not declare the parameters in the settings
generate_service_config_yaml_file()
SERVICE_YAML_TEMPLATE = (sys.path[-1] + "/onaptests/templates/vnf-services/" +
                         "basic-onboard-service.yaml")

try:
    # Try to retrieve the SERVICE NAME from the yaml file
    with open(SERVICE_YAML_TEMPLATE, "r") as yaml_template:
        yaml_config_file = load(yaml_template)
        SERVICE_NAME = next(iter(yaml_config_file.keys()))
except (FileNotFoundError, ValueError):
    raise onap_test_exceptions.TestConfigurationException

CLEANUP_FLAG = True
CLEANUP_ACTIVITY_TIMER = 10  # nb of seconds before cleanup in case cleanup option is set
VENDOR_NAME = "basic_onboard_vendor"

VF_NAME = "basic_onboard_vf"
VSP_NAME = "basic_onboard_vsp"

CLOUD_REGION_CLOUD_OWNER = "basic_onboard-cloud-owner"
CLOUD_REGION_TYPE = "openstack"
CLOUD_REGION_VERSION = "openstack"
CLOUD_OWNER_DEFINED_TYPE = "N/A"

AVAILABILITY_ZONE_NAME = "basic_onboard-availability-zone"
AVAILABILITY_ZONE_TYPE = "nova"
COMPLEX_PHYSICAL_LOCATION_ID = "lannion"
COMPLEX_DATA_CENTER_CODE = "1234-5"

GLOBAL_CUSTOMER_ID = "basic_onboard-customer"

OWNING_ENTITY = "basic_onboard-oe"
PROJECT = "basic_onboard-project"
LINE_OF_BUSINESS = "basic_onboard-lob"
PLATFORM = "basic_onboard-platform"

SERVICE_INSTANCE_NAME = "basic_onboard_service_instance"

# The cloud Part
# Assuming a cloud.yaml is available, use the openstack client
# to retrieve cloud info and avoid data duplication
TEST_CLOUD = os.getenv('OS_TEST_CLOUD')
cloud = openstack.connect(cloud=TEST_CLOUD)
VIM_USERNAME = cloud.config.auth.get('username','Fill me')
VIM_PASSWORD = cloud.config.auth.get('password','Fill me')
VIM_SERVICE_URL = cloud.config.auth.get('auth_url','Fill me')
TENANT_ID = cloud.config.auth.get('project_id','Fill me')
TENANT_NAME = cloud.config.auth.get('project_name','Fill me')
#CLOUD_REGION_ID = cloud.config.auth.get('region_name','RegionOne')
#CLOUD_DOMAIN = cloud.config.auth.get('project_domain_name','Default')
