import logging.config
import onaptests.utils.exceptions as onap_test_exceptions
from onapsdk.configuration import settings
from onaptests.steps.onboard.cps import CreateCpsAnchorStep, CreateCpsSchemaSetStep, CreateCpsDataspaceStep, CreateCpsAnchorNodeStep



if __name__ == "__main__":
    # logging configuration for onapsdk, it is not requested for onaptests
    # Correction requested in onapsdk to avoid having this duplicate code
    logging.config.dictConfig(settings.LOG_CONFIG)
    logger = logging.getLogger("Basic CPS")

    basic_cps = CreateCpsAnchorNodeStep(
        cleanup=settings.CLEANUP_FLAG)
    try:
        basic_cps.execute()
        basic_cps.cleanup()
    except onap_test_exceptions.TestConfigurationException:
        logger.error("Basic CPS configuration error")
    basic_cps.reports_collection.generate_report()
