"""Basic container commands to Docker."""
from typing import Dict
from grpc._channel import _InactiveRpcError
from pyhelm.chartbuilder import ChartBuilder
from pyhelm.tiller import Tiller
from onaptests.steps.base import BaseStep
from onaptests.utils.simulators import get_local_dir
from onaptests.configuration import settings
from onaptests.utils.exceptions import  (
    TestConfigurationException, EnvironmentPreparationException,
    EnvironmentCleanupException)



class HelmChartStep(BaseStep):
    """Basic operations on a docker container."""

    def __init__(self,  # pylint: disable=R0913
                 cleanup: bool = False,
                 namespace: str = 'default',
                 helm_repo_type: str = None,
                 release_name: str = None,
                 url: str = None) -> None:
        """Setup Helm chart configs, Tiller, and release name and path.

        Initialization example:
        simulator = HelmChartStep(
            cleanup=True,
            namespace="simulators",
            helm_repo_type="local",
            release_name="simulator")

        Arguments:
            cleanup (bool):
                determines if cleanup action should be called.
                Defaults to False.
            namespace (str):
                haelm chart destination namespace.
                Defaults to 'default'.
            helm_repo_type (str):
                'directory' or 'repo'. 'directory' is local. 'repo' is remote.
                Defaults to None.
            release_name (str):
                name of the chart folder and the name of chart installation.
                Defaults to None.
            release_name (str): remote's repo url if applicable.
                Defaults to None.
        """
        if not all([release_name, helm_repo_type]):
            raise TestConfigurationException("Provide release_name, repo type.")

        if helm_repo_type == "repo" and not url:
            raise TestConfigurationException("Provide URL to the remote repo.")

        super().__init__(cleanup=cleanup)

        self.release_name: str = release_name
        self.tiller = Tiller(settings.TILLER_HOST)

        chart_info = {
            "name": release_name,
            "source": {
                "type": helm_repo_type,
                "location": ""
            }
        }

        if helm_repo_type == 'directory':
            chart_info['source']['location'] = get_local_dir() / release_name
        elif helm_repo_type == 'repo':
            chart_info['source']['location'] = url

        self.chart: Dict = chart_info
        self.namespace: str = namespace

    @property
    def description(self) -> str:
        """Step description."""
        return "Execute Helm deployments."

    @property
    def component(self) -> str:
        """Component name."""
        return "Environment"

    @BaseStep.store_state
    def execute(self) -> None:
        """Execute helm deployment."""
        super().execute()
        chart = ChartBuilder(self.chart)
        try:
            self.tiller.install_release(
                chart=chart.get_helm_chart(),
                name=self.release_name,
                namespace=self.namespace,
                dry_run=False)
        except _InactiveRpcError as err:
            super().cleanup()
            msg = (err.details(), err.code())
            raise EnvironmentPreparationException(msg) from err


    def cleanup(self) -> None:
        """Remove helm deployment."""
        try:
            self.tiller.uninstall_release(release=self.release_name)
        except _InactiveRpcError as err:
            super().cleanup()
            raise EnvironmentCleanupException(err.details(), err.code()) from err
        super().cleanup()
