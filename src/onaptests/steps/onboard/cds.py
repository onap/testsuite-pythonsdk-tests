# http://www.apache.org/licenses/LICENSE-2.0
"""CDS onboard module."""

from abc import ABC
from pathlib import Path
from typing import Any, Dict

from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
from onapsdk.cds import Blueprint, DataDictionarySet
from onapsdk.cds.blueprint import Workflow
from onapsdk.cds.blueprint_processor import Blueprintprocessor
from onapsdk.configuration import settings
import urllib3

from ..base import BaseStep
from onaptests.utils.exceptions import OnapTestException


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
        config.load_kube_config(settings.K8S_CONFIG)
        self.k8s_client: client.CoreV1Api = client.CoreV1Api()

    @property
    def description(self) -> str:
        """Step description."""
        return "Expose CDS blueprintsprocessor NodePort."

    def is_service_node_port_type(self) -> bool:
        """Check if CDS blueprints processor service type is 'NodePort'

        Raises:
            OnapTestException: Kubernetes API error

        Returns:
            bool: True if service type is 'NodePort', False otherwise

        """
        try:
            service_data: Dict[str, Any] = self.k8s_client.read_namespaced_service(
                self.service_name,
                settings.K8S_ONAP_NAMESPACE
            )
            return service_data.spec.type == "NodePort"
        except ApiException:
            self._logger.exception("Kubernetes API exception")
            raise OnapTestException

    @BaseStep.store_state
    def execute(self) -> None:
        """Expose CDS blueprintprocessor port using kubernetes client.

        Use settings values:
         - K8S_CONFIG,
         - K8S_ONAP_NAMESPACE.

        """
        super().execute()
        if not self.is_service_node_port_type():
            try:
                self.k8s_client.patch_namespaced_service(
                    self.service_name,
                    settings.K8S_ONAP_NAMESPACE,
                    {"spec": {"ports": [{"port": 8080, "nodePort": 30449}], "type": "NodePort"}}
                )
            except ApiException:
                self._logger.exception("Kubernetes API exception")
                raise OnapTestException
            except urllib3.exceptions.HTTPError:
                self._logger.exception("Can't connect with k8s")
                raise OnapTestException
        else:
            self._logger.debug("Service already patched, skip")

    def cleanup(self) -> None:
        """Step cleanup.

        Restore CDS blueprintprocessor service.

        """
        if self.is_service_node_port_type():
            try:
                self.k8s_client.patch_namespaced_service(
                    self.service_name,
                    settings.K8S_ONAP_NAMESPACE,
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
            except ApiException:
                self._logger.exception("Kubernetes API exception")
                raise OnapTestException
            except urllib3.exceptions.HTTPError:
                self._logger.exception("Can't connect with k8s")
                raise OnapTestException
        else:
            self._logger.debug("Service is not 'NodePort' type, skip")
        return super().cleanup()


class BootstrapBlueprintprocessor(CDSBaseStep):
    """Bootstrap blueprintsprocessor."""

    def __init__(self, cleanup: bool = False) -> None:
        """Initialize step.

        Substeps:
            - ExposeCDSBlueprintprocessorNodePortStep.
        """
        super().__init__(cleanup=cleanup)
        self.add_step(ExposeCDSBlueprintprocessorNodePortStep(cleanup=cleanup))

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
        enriched: Blueprint = blueprint.enrich()
        enriched.save(settings.CDS_CBA_ENRICHED)

    @BaseStep.store_state(cleanup=True)
    def cleanup(self) -> None:
        """Cleanup enrichment step.

        Delete enriched CBA file.

        """
        super().cleanup()
        Path(settings.CDS_CBA_ENRICHED).unlink(missing_ok=True)


class CbaPublishStep(CDSBaseStep):
    """Publish CBA file step."""

    def __init__(self, cleanup=False) -> None:
        """Initialize CBA publish step."""
        super().__init__(cleanup=cleanup)
        self.add_step(CbaEnrichStep(cleanup=cleanup))

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

    def __init__(self, cleanup=False) -> None:
        """Initialize CBA process step."""
        super().__init__(cleanup=cleanup)
        self.add_step(CbaPublishStep(cleanup=cleanup))

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
