import logging.config
from onapsdk.configuration import settings
from onaptests.steps.instantiate.vf_module_ala_carte import YamlTemplateVfModuleAlaCarteInstantiateStep



if __name__ == "__main__":
    # logging configuration for onapsdk, it is not requested for onaptests
    # Correction requested in onapsdk to avoid having this duplicate code
    logging.config.dictConfig(settings.LOG_CONFIG)

    basic_vm_instantiate = YamlTemplateVfModuleAlaCarteInstantiateStep(cleanup=True)
    basic_vm_instantiate.execute()
