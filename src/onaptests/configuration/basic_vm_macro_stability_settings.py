from pathlib import Path

from onaptests.utils.resources import get_resource_location

from .basic_vm_macro_settings import *  # noqa

SERVICE_YAML_TEMPLATE = Path(get_resource_location(
    "templates/vnf-services/basic_vm_macro_stability-service.yaml"))
MODEL_YAML_TEMPLATE = None
