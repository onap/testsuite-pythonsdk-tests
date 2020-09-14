import logging.config
import time
from onapsdk.configuration import settings
from onaptests.steps.instantiate.vf_module_ala_carte import YamlTemplateVfModuleAlaCarteInstantiateStep



if __name__ == "__main__":
    # logging configuration for onapsdk, it is not requested for onaptests
    # Correction requested in onapsdk to avoid having this duplicate code
    logging.config.dictConfig(settings.LOG_CONFIG)
    logger = logging.getLogger("Instantiate Basic VM without multicloud")

    basic_vm_instantiate = YamlTemplateVfModuleAlaCarteInstantiateStep(
        cleanup=settings.CLEANUP_FLAG)
    basic_vm_instantiate.execute()
    if settings.CLEANUP_FLAG:
        time.sleep(settings.CLEANUP_ACTIVITY_TIMER)
        try:
            basic_vm_instantiate.cleanup()
        except ValueError as error:
            logger.info("service instance deleted as expected {0}".format(error))
