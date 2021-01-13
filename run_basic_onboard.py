import logging.config
import onaptests.utils.exceptions as onap_test_exceptions
from onapsdk.configuration import settings
from onaptests.steps.onboard.service import YamlTemplateServiceOnboardStep



if __name__ == "__main__":
    # logging configuration for onapsdk, it is not requested for onaptests
    # Correction requested in onapsdk to avoid having this duplicate code
    logging.config.dictConfig(settings.LOG_CONFIG)
    logger = logging.getLogger("Basic Onboard")

    basic_vm_onboard = YamlTemplateServiceOnboardStep(
        cleanup=settings.CLEANUP_FLAG)
    try:
        basic_vm_onboard.execute()
    except onap_test_exceptions.TestConfigurationException:
        logger.error("Basic Onboard configuration error")
    basic_vm_onboard.reports_collection.generate_report()
