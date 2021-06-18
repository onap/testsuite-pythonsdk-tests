from pathlib import Path
from uuid import uuid4

from .settings import *  # pylint: disable=W0614

ONLY_INSTANTIATE = False
CLEANUP_FLAG = True

VENDOR_NAME = "pnf_macro_vendor"
SERVICE_NAME = "test_pnf_macro"
SERVICE_INSTANCE_NAME = "TestPNFMacroInstantiation"
SERVICE_YAML_TEMPLATE = Path(Path(__file__).parent.parent,
                             "templates/vnf-services/pnf-service.yaml")

CDS_DD_FILE = Path(Path(__file__).parent.parent,
                   "templates/artifacts/dd.json")
CDS_CBA_UNENRICHED = Path(Path(__file__).parent.parent,
                          "templates/artifacts/PNF_DEMO.zip")
CDS_CBA_ENRICHED = "/tmp/PNF_DEMO_enriched.zip"

CLOUD_REGION_CLOUD_OWNER = "basicnf-owner" # must not contain _
CLOUD_REGION_ID = "k8sregion"
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

PNF_DEFINITION_ATRIFACT_FILE_PATH = Path(Path(__file__).parent.parent,
                                         "templates/artifacts/pnf-simulator.tar.gz")
PNF_RB_NAME = f"pnf-cnf-rb-{str(uuid4())}"
PNF_RB_VERSION = "v1"
PNF_PROFILE_ARTIFACT_FILE_PATH = Path(Path(__file__).parent.parent,
                                      "templates/artifacts/profile.tar.gz")
PNF_PROFILE_NAME = f"pnf-cnf-profile-{str(uuid4())}"
K8S_VERSION = "1.0"
K8S_CONFIG = str(Path(Path(__file__).parent.parent, "templates/artifacts/config"))

SERVICE_INSTANCE_NAME = "TestPNFMacroInstantiation"
<<<<<<< HEAD   (d04b13 [TEST] Use nf-simulator/vesclient)
=======

DCAE_VES_COLLECTOR_POD_NAME = "dcae-ves-collector"
PNF_WAIT_TIME = 60.0
PNF_REGISTRATION_NUMBER_OF_TRIES = 20
>>>>>>> CHANGE (fa58b9 [TEST] Wait for instantiated simulator longer)
