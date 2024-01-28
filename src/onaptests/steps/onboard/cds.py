# http://www.apache.org/licenses/LICENSE-2.0
"""CDS onboard module."""

from abc import ABC
from pathlib import Path
from typing import Any, Dict

from onapsdk.cds import Blueprint, DataDictionarySet
from onapsdk.cds.blueprint import Workflow
from onapsdk.cds.blueprint_processor import Blueprintprocessor
from onapsdk.configuration import settings

from onaptests.steps.base import BaseStep
from onaptests.steps.cloud.expose_service_node_port import \
    ExposeServiceNodePortStep
from onaptests.utils.exceptions import OnapTestException


class CDSBaseStep(BaseStep, ABC):
    """Abstract CDS base step."""

    @property
    def component(self) -> str:
        """Component name."""
        return "CDS"


class ExposeCDSBlueprintprocessorNodePortStep(CDSBaseStep, ExposeServiceNodePortStep):
    """Expose CDS blueprintsprocessor port."""
    def __init__(self) -> None:
        """Initialize step."""
        super().__init__(component="CDS",
                         service_name="cds-blueprints-processor-http",
                         port=8080,
                         node_port=settings.CDS_NODE_PORT)


class BootstrapBlueprintprocessor(CDSBaseStep):
    """Bootstrap blueprintsprocessor."""

    def __init__(self) -> None:
        """Initialize step.

        Substeps:
            - ExposeCDSBlueprintprocessorNodePortStep.
        """
        super().__init__(cleanup=BaseStep.HAS_NO_CLEANUP)
        if settings.EXPOSE_SERVICES_NODE_PORTS:
            self.add_step(ExposeCDSBlueprintprocessorNodePortStep())

    @property
    def description(self) -> str:
        """Step description."""
        return "Bootstrap CDS blueprintprocessor"

    @BaseStep.store_state
    def execute(self) -> None:
        """Bootsrap CDS blueprintprocessor."""
        super().execute()
        Blueprintprocessor.bootstrap()


class DataDictionaryUploadStep(CDSBaseStep):
    """Upload data dictionaries to CDS step."""

    def __init__(self) -> None:
        """Initialize data dictionary upload step."""
        super().__init__(cleanup=BaseStep.HAS_NO_CLEANUP)
        self.add_step(BootstrapBlueprintprocessor())

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

    def __init__(self) -> None:
        """Initialize CBA enrichment step."""
        super().__init__(cleanup=settings.CLEANUP_FLAG)
        self.add_step(DataDictionaryUploadStep())

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
        blueprint: Blueprint = Blueprint.load_from_file(settings.CDS_CBA_UNENRICHED)
        enriched: Blueprint = blueprint.enrich()
        enriched.save(settings.CDS_CBA_ENRICHED)

    @BaseStep.store_state(cleanup=True)
    def cleanup(self) -> None:
        """Cleanup enrichment step.

        Delete enriched CBA file.

        """
        Path(settings.CDS_CBA_ENRICHED).unlink()
        super().cleanup()


class CbaPublishStep(CDSBaseStep):
    """Publish CBA file step."""

    def __init__(self) -> None:
        """Initialize CBA publish step."""
        super().__init__(cleanup=BaseStep.HAS_NO_CLEANUP)
        # Let's skip enrichment if enriched CBA is already present
        if Path.is_file(settings.CDS_CBA_UNENRICHED):
            self.add_step(CbaEnrichStep())
        elif settings.EXPOSE_SERVICES_NODE_PORTS:
            self.add_step(ExposeCDSBlueprintprocessorNodePortStep())

    @property
    def description(self) -> str:
        """Step description."""
        return "Publish CBA file."

    @BaseStep.store_state
    def execute(self) -> None:
        """Publish CBA file.

        Use settings values:
         - CDS_CBA_ENRICHED.

        """
        super().execute()
        blueprint: Blueprint = Blueprint.load_from_file(settings.CDS_CBA_ENRICHED)
        blueprint.publish()


class CbaProcessStep(CDSBaseStep):
    """Process CBA step."""

    def __init__(self) -> None:
        """Initialize CBA process step."""
        super().__init__(cleanup=BaseStep.HAS_NO_CLEANUP)
        self.add_step(CbaPublishStep())

    @property
    def description(self) -> str:
        """Step description."""
        return "Process CBA file."

    @BaseStep.store_state
    def execute(self) -> None:
        """Process CBA file.

        Check if output is equal to expected

        Use settings values:
         - CDS_CBA_ENRICHED,
         - CDS_WORKFLOW_NAME,
         - CDS_WORKFLOW_INPUT

        """
        super().execute()
        blueprint: Blueprint = Blueprint.load_from_file(settings.CDS_CBA_ENRICHED)
        workflow: Workflow = blueprint.get_workflow_by_name(settings.CDS_WORKFLOW_NAME)
        output: Dict[str, Any] = workflow.execute(settings.CDS_WORKFLOW_INPUT)
        if not output == settings.CDS_WORKFLOW_EXPECTED_OUTPUT:
            raise OnapTestException("Response is not equal to the expected one")
