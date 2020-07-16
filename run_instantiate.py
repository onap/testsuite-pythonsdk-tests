#!/usr/bin/python
#
from onaptests.scenario import Scenario
import logging
import logging.config
import time
import sys
import pkg_resources

# Configure logging
logger = logging.getLogger("")
logger.setLevel(logging.DEBUG)
logname = "./onap_tests.debug.log"
fh = logging.FileHandler(logname)
fh_formatter = logging.Formatter(
     "%(asctime)s %(levelname)s %(lineno)d:%(filename)s(%(process)d) - %(message)s"
)
fh.setFormatter(fh_formatter)
logger.addHandler(fh)

ubuntu_scenario = Scenario(type = "ubuntu16test")
cloud = ubuntu_scenario.add_cloud_resources()
ubuntu_scenario.instantiate(instance_name="ubuntu16test-1",
                            cloud_resources=cloud,
                            service_name="ubuntu16test")