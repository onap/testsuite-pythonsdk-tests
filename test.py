import logging

from onaptests.steps.onboard.service import YamlTemplateServiceOnboardStep
from onaptests.steps.instantiate.service_ala_carte import YamlTemplateServiceAlaCarteInstantiateStep
from onaptests.steps.instantiate.vf_module_ala_carte import YamlTemplateVfModuleAlaCarteInstantiateStep


# Configure logging
logger = logging.getLogger("")
logger.setLevel(logging.INFO)
fh = logging.StreamHandler()
fh_formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s %(lineno)d:%(filename)s(%(process)d) - %(message)s"
)
fh.setFormatter(fh_formatter)
logger.addHandler(fh)


if __name__ == "__main__":
    vf_module_inst = YamlTemplateVfModuleAlaCarteInstantiateStep()
    vf_module_inst.execute()
