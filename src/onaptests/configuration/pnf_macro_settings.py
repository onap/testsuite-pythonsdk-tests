from pathlib import Path
from uuid import uuid4

from onaptests.utils.resources import get_resource_location
from .settings import *  # pylint: disable=W0614

ONLY_INSTANTIATE = False
CLEANUP_FLAG = True
USE_MULTICLOUD = False

VENDOR_NAME = "pnf_macro_vendor"
SERVICE_NAME = "test_pnf_macro"
SERVICE_INSTANCE_NAME = "TestPNFMacroInstantiation"
SERVICE_YAML_TEMPLATE = Path(get_resource_location("templates/vnf-services/pnf-service.yaml"))

CDS_DD_FILE = Path(get_resource_location("templates/artifacts/dd.json"))
CDS_CBA_UNENRICHED = Path(get_resource_location("templates/artifacts/PNF_DEMO.zip"))
CDS_CBA_ENRICHED = "/tmp/PNF_DEMO_enriched.zip"

CLOUD_REGION_CLOUD_OWNER = "basicnf-owner" # must not contain _
CLOUD_REGION_ID = "k8sregion-pnf-macro"
CLOUD_REGION_TYPE = "k8s"
CLOUD_REGION_VERSION = "1.0"
CLOUD_OWNER_DEFINED_TYPE = "N/A"
COMPLEX_PHYSICAL_LOCATION_ID = "sdktests"
GLOBAL_CUSTOMER_ID = "pnf_macrocustomer"
OWNING_ENTITY = "pnf_macro_owning_entity"
PROJECT = "pnf_macro_project"
LINE_OF_BUSINESS = "pnf_macro_line_of_business"
PLATFORM = "pnf_macro_platform"

INSTANTIATION_TIMEOUT = 600

MSB_K8S_DEFINITION_ATRIFACT_FILE_PATH = Path(get_resource_location("templates/artifacts/pnf-simulator.tar.gz"))
MSB_K8S_RB_NAME = f"pnf-cnf-rb-{str(uuid4())}"
MSB_K8S_RB_VERSION = "v1"
MSB_K8S_PROFILE_ARTIFACT_FILE_PATH = Path(get_resource_location("templates/artifacts/profile.tar.gz"))
MSB_K8S_PROFILE_NAME = f"pnf-cnf-profile-{str(uuid4())}"
K8S_VERSION = "1.0"
K8S_CONFIG = get_resource_location("templates/artifacts/config")
K8S_ADDITIONAL_RESOURCES_NAMESPACE = "onap-tests"

SERVICE_INSTANCE_NAME = f"TestPNFMacroInstantiation_{str(uuid4())}"

DCAE_VES_COLLECTOR_POD_NAME = "dcae-ves-collector"
PNF_WAIT_TIME = 60.0
PNF_REGISTRATION_NUMBER_OF_TRIES = 20

# Disable YAML SDC model definition which means all SDC config reside in SERVICE_YAML_TEMPLATE
MODEL_YAML_TEMPLATE = None
