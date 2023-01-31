# http://www.apache.org/licenses/LICENSE-2.0
"""PNF simulator registration module."""

import time
from typing import Tuple

import requests
from kubernetes import client, config, watch
from onapsdk.configuration import settings
import urllib3

from onaptests.steps.base import BaseStep
from onaptests.steps.instantiate.msb_k8s import CreateInstanceStep
from onaptests.utils.exceptions import EnvironmentPreparationException, OnapTestException


class PnfSimulatorCnfRegisterStep(BaseStep):
    """PNF simulator registration step."""

    def __init__(self, cleanup: bool = False) -> None:
        """Initialize step.

        Substeps:
            - CreateInstanceStep.
        """
        super().__init__(cleanup=cleanup)
        self.add_step(CreateInstanceStep(cleanup=cleanup))

    @property
    def description(self) -> str:
        """Step description."""
        return "Register PNF simulator with VES."

    @property
    def component(self) -> str:
        """Component name."""
        return "Environment"

    def is_pnf_pod_running(self, timeout_seconds=120) -> bool:
        """Check if PNF simulator pod is running.

        Args:
            timeout_seconds (int, optional): Timeout. Defaults to 120.

        Returns:
            bool: True if PNF simulator pod is running, False otherwise

        """
        config.load_kube_config(settings.K8S_CONFIG)
        k8s_client: "CoreV1API" = client.CoreV1Api()
        k8s_watch: "Watch" =  watch.Watch()
        try:
            for event in k8s_watch.stream(k8s_client.list_namespaced_pod,
                                        namespace=settings.K8S_ADDITIONAL_RESOURCES_NAMESPACE,
                                        timeout_seconds=timeout_seconds):
                if event["object"].metadata.name == "pnf-macro-test-simulator":
                    if not event["object"].status.phase in ["Pending", "Running"]:
                        # Invalid pod state
                        return False
                    return event["object"].status.phase == "Running"
            return False
        except urllib3.exceptions.HTTPError:
            self._logger.error("Can't connect with k8s")
            raise OnapTestException

    def get_ves_protocol_ip_and_port(self) -> Tuple[str, str, str]:
        """Static method to get VES protocol, ip address and port.

        Raises:
            EnvironmentPreparationException: VES pod is not running

        Returns:
            Tuple[str, str, str]: VES protocol, IP and port

        """
        config.load_kube_config(settings.K8S_CONFIG)
        k8s_client: "CoreV1API" = client.CoreV1Api()
        try:
            for service in k8s_client.list_namespaced_service(namespace=settings.K8S_ONAP_NAMESPACE).items:
                if service.metadata.name == settings.DCAE_VES_COLLECTOR_POD_NAME:
                    proto = "http"
                    if "443" in str(service.spec.ports[0].port):
                        proto = "https"
                    return proto, service.spec.cluster_ip, service.spec.ports[0].port
            raise EnvironmentPreparationException("Couldn't get VES protocol, ip and port")
        except Exception:
            self._logger.exception("Can't connect with k8s")
            raise OnapTestException

    @BaseStep.store_state
    def execute(self) -> None:
        """Send PNF registration event."""
        super().execute()
        if not self.is_pnf_pod_running():
            EnvironmentPreparationException("PNF simulator is not running")
        time.sleep(settings.PNF_WAIT_TIME)  # Let's still wait for PNF simulator to make sure it's initialized
        ves_proto, ves_ip, ves_port = self.get_ves_protocol_ip_and_port()
        registration_number: int = 0
        registered_successfully: bool = False
        while registration_number < settings.PNF_REGISTRATION_NUMBER_OF_TRIES and not registered_successfully:
            try:
                response = requests.post(
                    "http://portal.api.simpledemo.onap.org:30999/simulator/start",
                    json={
                        "simulatorParams": {
                            "repeatCount": 9999,
                            "repeatInterval": 30,
                            "vesServerUrl": f"{ves_proto}://sample1:sample1@{ves_ip}:{ves_port}/eventListener/v7"
                        },
                        "templateName": "registration.json",
                        "patch": {
                            "event": {
                                "commonEventHeader": {
                                    "sourceName": settings.SERVICE_INSTANCE_NAME
                                },
                                "pnfRegistrationFields": {
                                    "oamV4IpAddress": "192.168.0.1",
                                    "oamV6IpAddress": "2001:db8::1428:57ab"
                                }
                            }
                        }
                    }
                )
                response.raise_for_status()
                registered_successfully = True
                self._logger.info(f"PNF registered with {settings.SERVICE_INSTANCE_NAME} source name")
            except (requests.ConnectionError, requests.HTTPError) as http_error:
                self._logger.debug(f"Can't connect with PNF simulator: {str(http_error)}")
                registration_number = registration_number + 1
                time.sleep(settings.PNF_WAIT_TIME)
        if not registered_successfully:
            raise OnapTestException("PNF not registered successfully")
