import logging

from onaptests.components.instantiate.service_ala_carte import ServiceAlaCarteInstantiateComponent


# Configure logging
logger = logging.getLogger("")
logger.setLevel(logging.INFO)
fh = logging.StreamHandler()
fh_formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s %(lineno)d:%(filename)s(%(process)d) - %(message)s"
)
fh.setFormatter(fh_formatter)
logger.addHandler(fh)


if __name__ == "__main__":
    service_instantiate_scenario = ServiceAlaCarteInstantiateComponent(cleanup=False)
    service_instantiate_scenario.action()
