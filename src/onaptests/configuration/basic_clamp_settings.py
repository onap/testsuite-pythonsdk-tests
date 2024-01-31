from yaml import SafeLoader, load

from onaptests.utils.resources import get_resource_location

from .settings import *  # noqa

CLEANUP_FLAG = False
CLAMP_DISTRIBUTION_TIMER = 10

# The ONAP part
SERVICE_DETAILS = ("Onboarding, enriching a model with TCA." +
                   "Design a loop with Clamp and deploy it in Policy and DCAE")

VENDOR_NAME = "basiclamp_vendor"

VSP_NAME = "basiclamp_vsp"

OPERATIONAL_POLICIES = [
    {
        "name": "MinMax",
        "policy_type": "onap.policies.controlloop.guard.common.MinMax",
        "policy_version": "1.0.0",
        "config_function": "add_minmax_config",  # func
        "configuration": {
            "min": 1,
            "max": 10
        }
    },
    {
        "name": "FrequencyLimiter",
        "policy_type": "onap.policies.controlloop.guard.common.FrequencyLimiter",
        "policy_version": "1.0.0",
        "config_function": "add_frequency_limiter",  # func
        "configuration": {}
    }
]

# if a yaml file is define, retrieve info from this yaml files
# if not declare the parameters in the settings
SERVICE_YAML_TEMPLATE = get_resource_location("templates/vnf-services/basic_clamp-service.yaml")
CONFIGURATION_PATH = get_resource_location("configuration/")

try:
    # Try to retrieve the SERVICE NAME from the yaml file
    with open(SERVICE_YAML_TEMPLATE, "r", encoding="utf-8") as yaml_template:
        yaml_config_file = load(yaml_template, SafeLoader)
        SERVICE_NAME = next(iter(yaml_config_file.keys()))
        VF_NAME = SERVICE_NAME
except ValueError:
    SERVICE_NAME = ""  # Fill me
    VF_NAME = ""  # Fill me

MODEL_YAML_TEMPLATE = None
