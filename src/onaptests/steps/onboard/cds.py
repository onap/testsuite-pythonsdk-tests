# http://www.apache.org/licenses/LICENSE-2.0
"""CDS onboard module."""

from abc import ABC
from pathlib import Path
from typing import Optional

from kubernetes import client, config
from onapsdk.cds import Blueprint, DataDictionarySet
from onapsdk.cds.blueprint_processor import Blueprintprocessor
from onapsdk.configuration import settings

from ..base import BaseStep


class CDSBaseStep(BaseStep, ABC):
    """Abstract CDS base step."""

    @property
    def component(self) -> str:
        """Component name."""
        return "CDS"


class ExposeCDSBlueprintprocessorNodePortStep(CDSBaseStep):
    """Expose CDS blueprintsprocessor port."""

    def __init__(self, cleanup: bool) -> None:
        """Initialize step."""
        super().__init__(cleanup=cleanup)
        self.service_name: str = "cds-blueprints-processor-http"
        self.client: Optional[client.CoreV1Api] = None

    @property
    def description(self) -> str:
        """Step description."""
        return "Expose CDS blueprintsprocessor NodePort."

    @BaseStep.store_state
    def execute(self) -> None:
        """Expose CDS blueprintprocessor port using kubernetes client.

        Use settings values:
         - K8S_CONFIG,
         - K8S_NAMESPACE.

        """
        super().execute()
        config.load_kube_config(settings.K8S_CONFIG)
        self.k8s_client = client.CoreV1Api()
        self.k8s_client.patch_namespaced_service(
            self.service_name,
            settings.K8S_NAMESPACE,
            {"spec": {"ports": [{"port": 8080, "nodePort": 30449}], "type": "NodePort"}}
        )

    def cleanup(self) -> None:
        """Step cleanup.

        Restore CDS blueprintprocessor service.

        """
        self.k8s_client.patch_namespaced_service(
            self.service_name,
            settings.K8S_NAMESPACE,
            [
                {
                    "op": "remove",
                    "path": "/spec/ports/0/nodePort"
                },
                {
                    "op": "replace",
                    "path": "/spec/type",
                    "value": "ClusterIP"
                }
            ]
        )
        return super().cleanup()


class BootstrapBlueprintprocessor(CDSBaseStep):
    """Bootstrap blueprintsprocessor."""

    def __init__(self, cleanup: bool = False) -> None:
        super().__init__(cleanup=cleanup)
        self.add_step(ExposeCDSBlueprintprocessorNodePortStep(cleanup=cleanup))

    @property
    def description(self) -> str:
        """Step description."""
        return "Bootstrap CDS blueprintprocessor"

    @BaseStep.store_state
    def execute(self) -> None:
        """Bootsrap CDS blueprintprocessor"""
        super().execute()
        Blueprintprocessor.bootstrap()


class DataDictionaryUploadStep(CDSBaseStep):
    """Upload data dictionaries to CDS step."""

    def __init__(self, cleanup: bool = False) -> None:
        """Initialize data dictionary upload step."""
        super().__init__(cleanup=cleanup)
        self.add_step(BootstrapBlueprintprocessor(cleanup=cleanup))

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
        blueprint: Blueprint = Blueprint.load_from_file(settings.CDS_CBA_UNENRICHED)
        blueprint.enrich()
        blueprint.save(settings.CDS_CBA_ENRICHED)

    def cleanup(self) -> None:
        """Cleanup enrichment step.

        Delete enriched CBA file.

        """
        super().cleanup()
        Path(settings.CDA_CBA_ENRICHED).unlink()
