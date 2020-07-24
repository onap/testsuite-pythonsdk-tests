#!/usr/bin/python
#
from onaptests.clamp_scenario import ClampScenario
import logging
import logging.config



logger = logging.getLogger("")
logger.setLevel(logging.DEBUG)
logname = "./onap_tests.debug.log"
fh = logging.FileHandler(logname)
fh_formatter = logging.Formatter(
     "%(asctime)s %(levelname)s %(lineno)d:%(filename)s(%(process)d) - %(message)s"
)
fh.setFormatter(fh_formatter)
logger.addHandler(fh)


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
SERVICE_NAME = "ubuntu16test"

scenario = ClampScenario(service_name=SERVICE_NAME)
scenario.e2e(operational_policies=OPERATIONAL_POLICIES, delete=True)
