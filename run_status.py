import logging.config
import onaptests.utils.exceptions as onap_test_exceptions
from onapsdk.configuration import settings
from onaptests.scenario.status import Status


if __name__ == "__main__":
    # logging configuration for onapsdk, it is not requested for onaptests
    # Correction requested in onapsdk to avoid having this duplicate code
    logging.config.dictConfig(settings.LOG_CONFIG)
    logger = logging.getLogger("Status Check")

    status = Status()
    try:
        status.run()
        status.clean()
    except onap_test_exceptions.TestConfigurationException:
        logger.error("Status Check configuration error")
