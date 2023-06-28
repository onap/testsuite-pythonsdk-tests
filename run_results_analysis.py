import logging.config

import onaptests.utils.exceptions as onap_test_exceptions
from onapsdk.configuration import settings
from onaptests.scenario.result_analysis import ResultsAnalyser


if __name__ == "__main__":
    # logging configuration for onapsdk, it is not requested for onaptests
    # Correction requested in onapsdk to avoid having this duplicate code
    logging.config.dictConfig(settings.LOG_CONFIG)
    logger = logging.getLogger("Results Analysis")

    analysis = ResultsAnalyser()
    try:
        analysis.run()
        analysis.clean()
    except onap_test_exceptions.TestConfigurationException:
        logger.error("Results Analysis configuration error")