import logging.config
from onapsdk.configuration import settings

from onaptests.scenario.basic_sdnc import BasicSdnc
import onaptests.utils.exceptions as onap_test_exceptions

if __name__ == "__main__":
    # logging configuration for onapsdk, it is not requested for onaptests
    # Correction requested in onapsdk to avoid having this duplicate code
    logging.config.dictConfig(settings.LOG_CONFIG)
    logger = logging.getLogger("Basic SDNC")

    basic_sdnc = BasicSdnc(cleanup=settings.CLEANUP_FLAG)
    try:
        basic_sdnc.run()
        basic_sdnc.clean()
    except onap_test_exceptions.TestConfigurationException:
        logger.error("Basic SDNC configuration error")
