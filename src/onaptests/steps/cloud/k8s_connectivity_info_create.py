"""Connectivity info creation module."""
from jinja2 import Environment, PackageLoader, select_autoescape
from onapsdk.configuration import settings
from onapsdk.exceptions import APIError
from onapsdk.k8s import ConnectivityInfo

from onaptests.steps.base import BaseStep


class K8SConnectivityInfoStep(BaseStep):
    """CreateConnnectivityInfoStep."""

    def __init__(self):
        """Initialize step."""
        super().__init__(cleanup=settings.CLEANUP_FLAG)

    @property
    def description(self) -> str:
        """Step description."""
        return "Create K8S connectivity info."

    @property
    def component(self) -> str:
        """Component name."""
        return "K8S plugin"

    @BaseStep.store_state
    def execute(self):
        """Creation k8s connectivity information.

        Use settings values:
         - CLOUD_REGION_ID,
         - CLOUD_REGION_CLOUD_OWNER,
         - K8S_CONFIG.
        """
        super().execute()
        # Create Connectivity Info #########################################
        try:
            self._logger.info("Check if k8s connectivity information exists")
            ConnectivityInfo.get_connectivity_info_by_region_id(
                settings.CLOUD_REGION_ID)
        except APIError:
            if settings.IN_CLUSTER:
                token_file = "/var/run/secrets/kubernetes.io/serviceaccount/token"
                with open(token_file, "r", encoding="utf-8") as file:
                    user_token_value = file.read().strip()
                jinja_env = Environment(autoescape=select_autoescape(['json.j2']),
                                        loader=PackageLoader('onaptests.templates', 'kubeconfig'))
                kubeconfig_data = jinja_env.get_template("kube_config.json.j2").render(
                    user_token_value=user_token_value
                )
                # Create the k8s connectivity information with the kubeconfig data
                self._logger.info("Create the k8s connectivity information")
                ConnectivityInfo.create(settings.CLOUD_REGION_ID,
                                        settings.CLOUD_REGION_CLOUD_OWNER,
                                        kubeconfig_data.encode('utf-8'))
            else:
                self._logger.info("Create the k8s connectivity information")
                with open(settings.K8S_CONFIG, 'rb') as k8s_config:
                    ConnectivityInfo.create(settings.CLOUD_REGION_ID,
                                            settings.CLOUD_REGION_CLOUD_OWNER,
                                            k8s_config.read())

    @BaseStep.store_state(cleanup=True)
    def cleanup(self) -> None:
        """Cleanup K8S Connectivity information."""
        self._logger.info("Clean the k8s connectivity information")
        connectinfo = ConnectivityInfo.get_connectivity_info_by_region_id(
            settings.CLOUD_REGION_ID)
        connectinfo.delete()
        super().cleanup()
