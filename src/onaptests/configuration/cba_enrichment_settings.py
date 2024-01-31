from pathlib import Path

from onaptests.utils.resources import get_resource_location

from .settings import *  # noqa

SERVICE_NAME = "CDS blueprint enrichment"

SERVICE_DETAILS = "Tests CDS blueprint enrichment and its upload to blueprint processor"

CLEANUP_FLAG = True

CDS_DD_FILE = Path(get_resource_location("templates/artifacts/dd.json"))
CDS_CBA_UNENRICHED = Path(get_resource_location("templates/artifacts/PNF_DEMO.zip"))
CDS_CBA_ENRICHED = "/tmp/PNF_DEMO_enriched.zip"
