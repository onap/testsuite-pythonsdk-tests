"""Connectivity info creation module."""
from onapsdk.configuration import settings
from onapsdk.exceptions import APIError
from onapsdk.k8s import ConnectivityInfo
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from onapsdk.utils.jinja import jinja_env
from onaptests.steps.base import BaseStep
from jinja2 import Environment, PackageLoader, select_autoescape


class K8SConnectivityInfoStep(BaseStep):
    """CreateConnnectivityInfoStep."""

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
        ######## Create Connectivity Info #########################################
        try:
            self._logger.info("Check if k8s connectivity information exists")
            ConnectivityInfo.get_connectivity_info_by_region_id(
                settings.CLOUD_REGION_ID)
        except APIError:
            if settings.IN_CLUSTER:
                config.load_incluster_config()
                token_file = "/var/run/secrets/kubernetes.io/serviceaccount/token"
                with open(token_file, "r") as file:
                    user_token_value = file.read().strip()
                jinja_env = Environment(autoescape=select_autoescape(['json.j2']),
                                        loader=PackageLoader('onaptests.templates', 'kubeconfig'))
                kubeconfig_data = jinja_env.get_template("kube_config.json.j2").render(
                    user_token_value=user_token_value
                )
                kubeconfig_file_path = "kubeconfig"  # Specify the desired file path
                try:
                    with open(kubeconfig_file_path, "w") as file:
                        file.write(kubeconfig_data)
                    print(f"Kubeconfig file saved to: {kubeconfig_file_path}")
                except OSError as e:
                    print(f"Error saving kubeconfig file: {e}")
                # Create the k8s connectivity information with the kubeconfig data
                self._logger.info("Create the k8s connectivity information")
                ConnectivityInfo.create(settings.CLOUD_REGION_ID,
                                        settings.CLOUD_REGION_CLOUD_OWNER,
                                        open(kubeconfig_file_path, 'rb').read())
            else:
                self._logger.info("Create the k8s connectivity information")
                ConnectivityInfo.create(settings.CLOUD_REGION_ID,
                                        settings.CLOUD_REGION_CLOUD_OWNER,
                                        open(settings.K8S_CONFIG, 'rb').read())

    @BaseStep.store_state(cleanup=True)
    def cleanup(self) -> None:
        """Cleanup K8S Connectivity information."""
        self._logger.info("Clean the k8s connectivity information")
        connectinfo = ConnectivityInfo.get_connectivity_info_by_region_id(
            settings.CLOUD_REGION_ID)
        connectinfo.delete()
        super().cleanup()
