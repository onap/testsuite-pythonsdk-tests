import logging.config
from onapsdk.configuration import settings
from onaptests.steps.instantiate.vl_ala_carte import YamlTemplateVlAlaCarteInstantiateStep



if __name__ == "__main__":
    # logging configuration for onapsdk, it is not requested for onaptests
    # Correction requested in onapsdk to avoid having this duplicate code
    logging.config.dictConfig(settings.LOG_CONFIG)

    basic_network_instantiate = YamlTemplateVlAlaCarteInstantiateStep()
    basic_network_instantiate.execute()
