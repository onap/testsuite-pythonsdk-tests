"""Connectivity info creation module."""
from onapsdk.configuration import settings
from onapsdk.exceptions import APIError
from onapsdk.k8s import ConnectivityInfo
from kubernetes import client, config
from ..base import BaseStep

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
            ConnectivityInfo.get_connectivity_info_by_region_id(settings.CLOUD_REGION_ID)
        except APIError:
            if settings.IN_CLUSTER:
                config.load_incluster_config()
            else:
                if settings.K8S_CONFIG:
                    config.load_kube_config(config_file=settings.K8S_CONFIG)
                else:
                    config.load_kube_config()
            self._logger.info("Create the k8s connectivity information")
            ConnectivityInfo.create(settings.CLOUD_REGION_ID,
                                    settings.CLOUD_REGION_CLOUD_OWNER,
                                    open(settings.K8S_CONFIG, 'rb').read())

    @BaseStep.store_state(cleanup=True)
    def cleanup(self) -> None:
        """Cleanup K8S Connectivity information."""
        self._logger.info("Clean the k8s connectivity information")
        connectinfo = ConnectivityInfo.get_connectivity_info_by_region_id(settings.CLOUD_REGION_ID)
        connectinfo.delete()
        super().cleanup()
