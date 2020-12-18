import logging.config
import time
import onaptests.utils.exceptions as onap_test_exceptions
from onaptests.configuration import settings
from onaptests.steps.instantiate.vf_module_ala_carte import YamlTemplateVfModuleAlaCarteInstantiateStep



if __name__ == "__main__":
    # logging configuration for onapsdk, it is not requested for onaptests
    # Correction requested in onapsdk to avoid having this duplicate code
    logging.config.dictConfig(settings.LOG_CONFIG)
    logger = logging.getLogger("Instantiate Basic VM without multicloud")

    basic_vm_instantiate = YamlTemplateVfModuleAlaCarteInstantiateStep(
        cleanup=settings.CLEANUP_FLAG)
    try:
        basic_vm_instantiate.execute()
        if settings.CLEANUP_FLAG:
            time.sleep(settings.CLEANUP_ACTIVITY_TIMER)
            basic_vm_instantiate.cleanup()
    except onap_test_exceptions.TestConfigurationException:
        logger.error("Basic VM configuration error")
    except onap_test_exceptions.ServiceInstantiateException:
        logger.error("Basic VM instantiation error")
    except onap_test_exceptions.ServiceCleanupException:
        logger.error("Basic VM instance cleanup error")
    except onap_test_exceptions.VnfInstantiateException:
        logger.error("Basic VM Vnf instantiation error")
    except onap_test_exceptions.VnfCleanupException:
        logger.error("Basic VM Vnf instance cleanup error")
    except onap_test_exceptions.VfModuleInstantiateException:
        logger.error("Basic VM Module instantiation error")
    except onap_test_exceptions.VfModuleCleanupException:
        logger.error("Basic VM Module cleanup error")

    basic_vm_instantiate.reports_collection.generate_report()
