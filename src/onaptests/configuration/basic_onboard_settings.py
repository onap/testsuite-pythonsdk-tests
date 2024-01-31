

from yaml import SafeLoader, load

import onaptests.utils.exceptions as onap_test_exceptions
from onaptests.utils.resources import get_resource_location

from .settings import *  # noqa


# The ONAP part
SERVICE_DETAILS = "Basic onboard service to only onboard a service in SDC"

# USE_MULTICLOUD = False
# Set ONLY_INSTANTIATE to true to run an instantiation without repeating
# onboarding and related AAI configuration (Cloud config)
# ONLY_INSTANTIATE= False

# if a yaml file is define, retrieve info from this yaml files
# if not declare the parameters in the settings

MODEL_YAML_TEMPLATE = None
CLEANUP_FLAG = True
SDC_CLEANUP = True

SERVICE_YAML_TEMPLATE = get_resource_location("templates/vnf-services/basic-onboard-service.yaml")
generate_service_config_yaml_file(service_name="basic_onboard",  # noqa
                                  service_template="basic_onboard-service.yaml.j2",
                                  service_config=SERVICE_YAML_TEMPLATE,
                                  generate_random_names=SDC_CLEANUP)

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
