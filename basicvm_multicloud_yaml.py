import logging.config
from onapsdk.configuration import settings
from onaptests.steps.instantiate.service_ala_carte import YamlTemplateServiceAlaCarteInstantiateStep



if __name__ == "__main__":
    # logging configuration for onapsdk, it is not requested for onaptests
    # Correction requested in onapsdk to avoid having this duplicate code
    logging.config.dictConfig(settings.LOG_CONFIG)

    service_inst = YamlTemplateServiceAlaCarteInstantiateStep()
    #service_inst = ServiceAlaCarteInstantiateStep()
    service_inst.execute()
