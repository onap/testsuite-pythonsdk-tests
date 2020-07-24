#!/usr/bin/python
#
from onaptests.closed_loop import ClosedLoop
import logging
import logging.config
import os
import time
import sys
import pkg_resources


logger = logging.getLogger("")
logger.setLevel(logging.DEBUG)
logname = "./onap_tests.debug.log"
fh = logging.FileHandler(logname)
fh_formatter = logging.Formatter(
     "%(asctime)s %(levelname)s %(lineno)d:%(filename)s(%(process)d) - %(message)s"
)
fh.setFormatter(fh_formatter)
logger.addHandler(fh)


SERVICE_NAME = "my_service"

scenario = ClosedLoop(service_name=SERVICE_NAME) # onboard a a service with 1 vm ubuntu 
scenario.e2e(delete=False)
