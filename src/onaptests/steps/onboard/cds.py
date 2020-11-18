# http://www.apache.org/licenses/LICENSE-2.0
"""CDS onboard module."""

from abc import ABC
from pathlib import Path

from onapsdk.cds import Blueprint, DataDictionarySet
from onapsdk.configuration import settings

from ..base import BaseStep


class CDSBaseStep(BaseStep, ABC):
    """Abstract CDS base step."""

    @property
    def component(self) -> str:
        """Component name."""
        return "CDS"


class DataDictionaryUploadStep(CDSBaseStep):
    """Upload data dictionaries to CDS step."""

    @property
    def description(self) -> str:
        """Step description."""
        return "Upload data dictionaries to CDS."

    @BaseStep.store_state
    def execute(self) -> None:
        """Upload data dictionary to CDS.

        Use settings values:
         - CDS_DD_FILE.

        """
        super().execute()
        dd_set: DataDictionarySet = DataDictionarySet.load_from_file(settings.CDS_DD_FILE)
        dd_set.upload()


class CbaEnrichStep(CDSBaseStep):
    """Enrich CBA file step."""

    def __init__(self, cleanup=False) -> None:
        """Initialize CBA enrichment step."""
        super().__init__(cleanup=cleanup)
        self.add_step(DataDictionaryUploadStep(cleanup=cleanup))

    @property
    def description(self) -> str:
        """Step description."""
        return "Enrich CBA file."

    @BaseStep.store_state
    def execute(self) -> None:
        """Enrich CBA file.

        Use settings values:
         - CDS_DD_FILE.

        """
        super().execute()
        blueprint: Blueprint = Blueprint.load_from_file(settings.CDS_CBA_UNERICHED)
        blueprint.enrich()
        blueprint.save(settings.CDA_CBA_ENRICHED)

    def cleanup(self) -> None:
        """Cleanup enrichment step.

        Delete enriched CBA file.

        """
        super().cleanup()
        Path(settings.CDA_CBA_ENRICHED).unlink()
