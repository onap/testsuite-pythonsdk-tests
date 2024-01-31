
import random
import string

from jinja2 import Environment, PackageLoader
from yaml import SafeLoader, load

import onaptests.utils.exceptions as onap_test_exceptions
from onaptests.utils.resources import get_resource_location

from .settings import *  # noqa


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

    with open(SERVICE_YAML_TEMPLATE, 'w+', encoding="utf-8") as file_to_write:
        file_to_write.write(rendered_template)


# The ONAP part
SERVICE_DETAILS = "Basic onboard service to only onboard a service in SDC"

# USE_MULTICLOUD = False
# Set ONLY_INSTANTIATE to true to run an instantiation without repeating
# onboarding and related AAI configuration (Cloud config)
# ONLY_INSTANTIATE= False

# if a yaml file is define, retrieve info from this yaml files
# if not declare the parameters in the settings

SERVICE_YAML_TEMPLATE = get_resource_location("templates/vnf-services/basic-onboard-service.yaml")
generate_service_config_yaml_file()

try:
    # Try to retrieve the SERVICE NAME from the yaml file
    with open(SERVICE_YAML_TEMPLATE, "r", encoding="utf-8") as yaml_template:
        yaml_config_file = load(yaml_template, SafeLoader)
        SERVICE_NAME = next(iter(yaml_config_file.keys()))
except (FileNotFoundError, ValueError) as exc:
    raise onap_test_exceptions.TestConfigurationException from exc

# CLEANUP_FLAG = True
# CLEANUP_ACTIVITY_TIMER = 10  # nb of seconds before cleanup in case cleanup option is set
VENDOR_NAME = "basic_onboard_vendor"

MODEL_YAML_TEMPLATE = None
CLEANUP_FLAG = True
