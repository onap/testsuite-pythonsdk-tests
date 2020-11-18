from pathlib import Path

from .settings import *

SERVICE_NAME = "CDS blueprint enrichment"

CLEANUP_FLAG = True

CDS_DD_FILE = Path(Path(__file__).parent.parent, "templates/artifacts/dd.json")
CDS_CBA_UNENRICHED = Path(Path(__file__).parent.parent, "templates/artifacts/PNF_DEMO.zip")
CDS_CBA_ENRICHED = "/tmp/vLB_enriched.zip"
