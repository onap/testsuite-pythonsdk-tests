import logging.config
import time
import onaptests.utils.exceptions as onap_test_exceptions
from onapsdk.configuration import settings
from onaptests.steps.onboard.service import YamlTemplateServiceOnboardStep



if __name__ == "__main__":
    # logging configuration for onapsdk, it is not requested for onaptests
    # Correction requested in onapsdk to avoid having this duplicate code
    logging.config.dictConfig(settings.LOG_CONFIG)
    logger = logging.getLogger("Basic Onboard without multicloud")

    basic_vm_onboard = YamlTemplateServiceOnboardStep(
        cleanup=settings.CLEANUP_FLAG)
    try:
        basic_vm_onboard.execute()
        if settings.CLEANUP_FLAG:
            time.sleep(settings.CLEANUP_ACTIVITY_TIMER)
            basic_vm_onboard.cleanup()
    except onap_test_exceptions.TestConfigurationException:
        logger.error("Basic Onboard configuration error")
    except onap_test_exceptions.ServiceInstantiateException:
        logger.error("Basic Onboard instantiation error")
    except onap_test_exceptions.ServiceCleanupException:
        logger.error("Basic Onboard instance cleanup error")
    except onap_test_exceptions.VnfInstantiateException:
        logger.error("Basic Onboard Vnf instantiation error")
    except onap_test_exceptions.VnfCleanupException:
        logger.error("Basic Onboard Vnf instance cleanup error")
    except onap_test_exceptions.VfModuleInstantiateException:
        logger.error("Basic Onboard Module instantiation error")
    except onap_test_exceptions.VfModuleCleanupException:
        logger.error("Basic Onboard Module cleanup error")

    basic_vm_onboard.reports_collection.generate_report()
