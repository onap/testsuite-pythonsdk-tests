import logging

from onaptests.steps.onboard.service import YamlTemplateServiceOnboardStep


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
    service_onboard = YamlTemplateServiceOnboardStep()
    service_onboard.execute()
