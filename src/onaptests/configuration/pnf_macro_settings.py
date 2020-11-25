from pathlib import Path

# from onapsdk.configuration import settings as onapsdk_settings

from .settings import *

ONLY_INSTANTIATE = False
CLEANUP_FLAG = True

VENDOR_NAME = "pnf_macro_vendor"
SERVICE_NAME = "test_pnf_macro"
SERVICE_INSTANCE_NAME = "TestPNFMacroInstantiation"
SERVICE_YAML_TEMPLATE = Path(Path(__file__).parent.parent, "templates/vnf-services/pnf-service.yaml")

CDS_DD_FILE = Path(Path(__file__).parent.parent, "templates/artifacts/dd.json")
CDS_CBA_UNENRICHED = Path(Path(__file__).parent.parent, "templates/artifacts/PNF_DEMO.zip")
CDS_CBA_ENRICHED = "/tmp/PNF_DEMO_enriched.zip"

GLOBAL_CUSTOMER_ID = "pnf_macrocustomer"
OWNING_ENTITY = "pnf_macro_owning_entity"
PROJECT = "pnf_macro_project"
LINE_OF_BUSINESS = "pnf_macro_line_of_business"
PLATFORM = "pnf_macro_platform"

INSTANTIATION_TIMEOUT = 600

PNF_VES_CONFIG = dict(
            count=1,
            vesprotocol="https",
            vesip="",  # Due to it's not possible to get these value from SDK settings now it's going to be updated later
            vesport="",  # Due to it's not possible to get these value from SDK settings now it's going to be updated later
            vesresource="eventListener",
            vesversion="v7",
            ipstart="10.11.0.16",
            user="sample1",
            password="sample1",
            ipfileserver="127.0.0.1",
            typefileserver="sftp",
)
PNF_CUSTOM_DATA = dict(
    commonEventHeaderParams=dict(
        sourceName=SERVICE_INSTANCE_NAME,
        reportingEntityName=SERVICE_INSTANCE_NAME
    )
)
