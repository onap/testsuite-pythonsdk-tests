# http://www.apache.org/licenses/LICENSE-2.0
"""Expose service NodePort module."""

from typing import Any, Dict

import urllib3
from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
from onapsdk.configuration import settings

from onaptests.steps.base import BaseStep
from onaptests.utils.exceptions import OnapTestException


class ExposeServiceNodePortStep(BaseStep):
    """Expose Service NodePort."""

    def __init__(self, component: str, service_name: str, port: int, node_port: int) -> None:
        """Initialize step."""
        super().__init__(cleanup=settings.CLEANUP_FLAG)
        self.component_value = component
        self.service_name = service_name
        self.port = port
        self.node_port = node_port
        self.k8s_client: client.CoreV1Api = None

    @property
    def component(self) -> str:
        return self.component_value

    @property
    def description(self) -> str:
        """Step description."""
        return "Expose service NodePort."

    def is_service_node_port_type(self) -> bool:
        """Check if service type is 'NodePort'

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
        except ApiException as exc:
            self._logger.exception("Kubernetes API exception")
            raise OnapTestException from exc

    @BaseStep.store_state
    def execute(self) -> None:
        """Expose services ports using kubernetes client.

        Use settings values:
         - K8S_CONFIG,
         - K8S_ONAP_NAMESPACE.
         - EXPOSE_SERVICES_NODE_PORTS

        """
        super().execute()
        if settings.IN_CLUSTER:
            config.load_incluster_config()
        else:
            config.load_kube_config(config_file=settings.K8S_CONFIG)
        self.k8s_client: client.CoreV1Api = client.CoreV1Api()
        if not self.is_service_node_port_type():
            try:
                self.k8s_client.patch_namespaced_service(
                    self.service_name,
                    settings.K8S_ONAP_NAMESPACE,
                    {"spec": {"ports": [{"port": self.port,
                                         "nodePort": self.node_port}],
                              "type": "NodePort"}}
                )
            except ApiException as exc:
                self._logger.exception("Kubernetes API exception")
                raise OnapTestException from exc
            except urllib3.exceptions.HTTPError as exc:
                self._logger.exception("Can't connect with k8s")
                raise OnapTestException from exc
        else:
            self._logger.debug("Service already patched, skip")

    @BaseStep.store_state(cleanup=True)
    def cleanup(self) -> None:
        """Step cleanup.

        Restore service.

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
            except ApiException as exc:
                self._logger.exception("Kubernetes API exception")
                raise OnapTestException from exc
            except urllib3.exceptions.HTTPError as exc:
                self._logger.exception("Can't connect with k8s")
                raise OnapTestException from exc
        else:
            self._logger.debug("Service is not 'NodePort' type, skip")
        return super().cleanup()
