import logging.config
import time
import onaptests.utils.exceptions as onap_test_exceptions
from onapsdk.configuration import settings
from onaptests.scenario.multi_vnf_macro import MultiVnfUbuntuMacroStep

if __name__ == "__main__":
    # logging configuration for onapsdk, it is not requested for onaptests
    # Correction requested in onapsdk to avoid having this duplicate code
    logging.config.dictConfig(settings.LOG_CONFIG)
    logger = logging.getLogger("Instantiate Ubuntu multi VNF without multicloud")
    step = MultiVnfUbuntuMacroStep(cleanup=settings.CLEANUP_FLAG)
    try:
        step.execute()
        if settings.CLEANUP_FLAG:
            logger.info("Starting to clean up in {} seconds".format(settings.CLEANUP_ACTIVITY_TIMER))
            time.sleep(settings.CLEANUP_ACTIVITY_TIMER)
            step.cleanup()
    except onap_test_exceptions.TestConfigurationException:
        logger.error("Ubuntu NSO VM configuration error")
    except onap_test_exceptions.ServiceInstantiateException:
        logger.error("Ubuntu NSO VM instantiation error")
    except onap_test_exceptions.ServiceCleanupException:
        logger.error("Ubuntu NSO VM instance cleanup error")
    except onap_test_exceptions.VnfInstantiateException:
        logger.error("Ubuntu NSO VM Vnf instantiation error")
    except onap_test_exceptions.VnfCleanupException:
        logger.error("Ubuntu NSO VM Vnf instance cleanup error")
    except onap_test_exceptions.VfModuleInstantiateException:
        logger.error("Ubuntu NSO VM Module instantiation error")
    except onap_test_exceptions.VfModuleCleanupException:
        logger.error("Ubuntu NSO VM Module cleanup error")
