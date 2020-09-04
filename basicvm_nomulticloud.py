# import logging

from onaptests.steps.instantiate.module import ModuleInstantiateStep

# from onapsdk.sdc.vendor import Vendor


# Configure logging
# logger = logging.getLogger("")
# logger.setLevel(logging.INFO)
# fh = logging.StreamHandler()
# fh_formatter = logging.Formatter(
#     "%(asctime)s %(levelname)s %(name)s %(lineno)d:%(filename)s(%(process)d) - %(message)s"
# )
# fh.setFormatter(fh_formatter)
# logger.addHandler(fh)
# Vendor.set_proxy({ 'http': 'socks5h://127.0.0.1:8083', 'https': 'socks5h://127.0.0.1:8083'})


if __name__ == "__main__":
    basic_vm_instantiate = ModuleInstantiateStep()
    basic_vm_instantiate.execute()
    # service_onboard = YamlTemplateServiceOnboardStep()
    # service_onboard.execute()
