import os
import sys
from yaml import load

from pathlib import Path

from .settings import * # pylint: disable=W0614

""" Specific Basic clamp settings."""
CLEANUP_FLAG = False
CLAMP_DISTRIBUTION_TIMER = 10
VENDOR_NAME = "basiclamp_vendor"

VSP_NAME = "basiclamp_vsp"

OPERATIONAL_POLICIES = [
  {
    "name": "MinMax",
    "policy_type": "onap.policies.controlloop.guard.common.MinMax",
    "policy_version": "1.0.0",
    "config_function": "add_minmax_config", #func
    "configuration": {
      "min": 1,
      "max": 10
    }
  },
  {
    "name": "FrequencyLimiter",
    "policy_type": "onap.policies.controlloop.guard.common.FrequencyLimiter",
    "policy_version": "1.0.0",
    "config_function": "add_frequency_limiter", #func
    "configuration": {}
  }
]

CERT = (Path.cwd() / 'cert.pem', Path.cwd() / 'cert.key')
# SERVICE_NAME = "ubuntu18agent"

# if a yaml file is define, retrieve info from this yaml files
# if not declare the parameters in the settings
SERVICE_YAML_TEMPLATE = (sys.path[-1] + "/onaptests/templates/vnf-services/" +
                         "ubuntu18agent-service.yaml")
CONFIGURATION_PATH = sys.path[-1] + "/onaptests/configuration/"

try:
    # Try to retrieve the SERVICE NAME from the yaml file
    with open(SERVICE_YAML_TEMPLATE, "r") as yaml_template:
        yaml_config_file = load(yaml_template)
        SERVICE_NAME = next(iter(yaml_config_file.keys()))
        VF_NAME = SERVICE_NAME
except ValueError:
    SERVICE_NAME = "" # Fill me
    VF_NAME = "" # Fill me
