import logging.config
import onaptests.utils.exceptions as onap_test_exceptions
from onapsdk.configuration import settings
from onaptests.steps.cloud.check_status import CheckNamespaceStatusStep



if __name__ == "__main__":
    # logging configuration for onapsdk, it is not requested for onaptests
    # Correction requested in onapsdk to avoid having this duplicate code
    logging.config.dictConfig(settings.LOG_CONFIG)
    logger = logging.getLogger("Status Check")

    status = CheckNamespaceStatusStep(
        cleanup=settings.CLEANUP_FLAG, dir_result="src")
    try:
        status.execute()
        status.cleanup()
    except onap_test_exceptions.TestConfigurationException:
        logger.error("Status Check configuration error")
    status.reports_collection.generate_report()