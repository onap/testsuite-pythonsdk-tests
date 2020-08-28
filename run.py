import logging
from onaptests.steps.instantiate.service_ala_carte import ServiceAlaCarteInstantiateStep

# logging configuration for onapsdk, it is not requested for onaptests
# Correction requested in onapsdk to avoid having this duplicate code 
# This code is set based on settings in base.py
logger = logging.getLogger("")
logger.setLevel(logging.DEBUG)
fh = logging.StreamHandler()
fh_formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s %(lineno)d:%(filename)s(%(process)d) - %(message)s"
)
fh.setFormatter(fh_formatter)
logger.addHandler(fh)

file_handler = logging.FileHandler("./debug.log")
file_handler.setFormatter(fh_formatter)
logger.addHandler(file_handler)

if __name__ == "__main__":
    service_inst = ServiceAlaCarteInstantiateStep()
    service_inst.execute()
