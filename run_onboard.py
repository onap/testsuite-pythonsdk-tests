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
logname = "/home/ngsl7698/tests/pythonsdk-tests/onap_tests.debug.log"
fh = logging.FileHandler(logname)
fh_formatter = logging.Formatter(
     "%(asctime)s %(levelname)s %(lineno)d:%(filename)s(%(process)d) - %(message)s"
)
fh.setFormatter(fh_formatter)
logger.addHandler(fh)

ubuntu_scenario = Scenario(type = "ubuntu16test")
ubuntu_scenario.onboard(ubuntu_scenario.scenario_name)