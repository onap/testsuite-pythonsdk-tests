# http://www.apache.org/licenses/LICENSE-2.0
"""PNF simulator registration module."""

import time
from typing import Tuple

import requests
from kubernetes import client, config, watch
from onapsdk.configuration import settings

from onaptests.steps.base import BaseStep
from onaptests.steps.instantiate.msb_k8s import CreateInstanceStep
from onaptests.utils.exceptions import EnvironmentPreparationException


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

    @staticmethod
    def is_pnf_pod_running(timeout_seconds=120) -> bool:
        """Check if PNF simulator pod is running.

        Args:
            timeout_seconds (int, optional): Timeout. Defaults to 120.

        Returns:
            bool: True if PNF simulator pod is running, False otherwise

        """
        config.load_kube_config(settings.K8S_CONFIG)
        k8s_client: "CoreV1API" = client.CoreV1Api()
        k8s_watch: "Watch" =  watch.Watch()
        for event in k8s_watch.stream(k8s_client.list_namespaced_pod,
                                      namespace=settings.K8S_NAMESPACE,
                                      timeout_seconds=timeout_seconds):
            if event["object"].metadata.name == "pnf-simulator":
                if not event["object"].status.phase in ["Pending", "Running"]:
                    # Invalid pod state
                    return False
                return event["object"].status.phase == "Running"
        return False

    @staticmethod
    def get_ves_ip_and_port() -> Tuple[str, str]:
        """Static method to get VES ip address and port.

        Raises:
            EnvironmentPreparationException: VES pod is not running

        Returns:
            Tuple[str, str]: VES IP and port

        """
        config.load_kube_config(settings.K8S_CONFIG)
        k8s_client: "CoreV1API" = client.CoreV1Api()
        for service in k8s_client.list_namespaced_service(namespace=settings.K8S_NAMESPACE).items:
            if service.metadata.name == "xdcae-ves-collector":
                return service.spec.cluster_ip, service.spec.ports[0].port
        raise EnvironmentPreparationException("Couldn't get VES ip and port")

    @BaseStep.store_state
    def execute(self) -> None:
        """Send PNF registration event."""
        super().execute()
        if not self.is_pnf_pod_running():
            EnvironmentPreparationException("PNF simulator is not running")
        time.sleep(30.0)  # Let's still wait for PNF simulator to make sure it's initialized
        ves_ip, ves_port = self.get_ves_ip_and_port()
        response = requests.post(
            "http://portal.api.simpledemo.onap.org:30999/simulator/event",
            json={
                "vesServerUrl": f"https://{ves_ip}:{ves_port}/eventListener/v7",
                "event": {
                    "event": {
                        "commonEventHeader": {
                            "domain": "pnfRegistration",
                            "eventId": "ORAN_SIM_400600927_2020-04-02T17:20:22.2Z",
                            "eventName": "pnfRegistration",
                            "eventType": "EventType5G",
                            "sequence": 0,
                            "priority": "Low",
                            "reportingEntityId": "",
                            "reportingEntityName": "ORAN_SIM_400600927",
                            "sourceId": "",
                            "sourceName": settings.SERVICE_INSTANCE_NAME,
                            "startEpochMicrosec": 94262132085746,
                            "lastEpochMicrosec": 94262132085746,
                            "nfNamingCode": "sdn controller",
                            "nfVendorName": "sdn",
                            "timeZoneOffset": "+00:00",
                            "version": "4.0.1",
                            "vesEventListenerVersion": "7.0.1"
                        },
                        "pnfRegistrationFields": {
                            "pnfRegistrationFieldsVersion": "2.0",
                            "lastServiceDate": "2019-08-16",
                            "macAddress": "D7:64:C8:CC:E9:32",
                            "manufactureDate": "2019-08-16",
                            "modelNumber": "Simulated Device",
                            "oamV4IpAddress": "172.30.1.6",
                            "oamV6IpAddress": "0:0:0:0:0:ffff:a0a:011",
                            "serialNumber": "Simulated Device",
                            "softwareVersion": "2.3.5",
                            "unitFamily": "Simulated Device",
                            "unitType": "ntsim_oran",
                            "vendorName": "Melacon",
                            "additionalFields": {
                                "oamPort": "830",
                                "protocol": "SSH",
                                "username": "netconf",
                                "password": "netconf",
                                "reconnectOnChangedSchema": "false",
                                "sleep-factor": "1.5",
                                "tcpOnly": "false",
                                "connectionTimeout": "20000",
                                "maxConnectionAttempts": "100",
                                "betweenAttemptsTimeout": "2000",
                                "keepaliveDelay": "120"
                            }
                        }
                    }
                }
            }
        )
        response.raise_for_status()
