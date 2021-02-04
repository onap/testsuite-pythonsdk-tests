"""Basic container commands to Docker."""
from typing import Dict
from pathlib import Path
import yaml
from grpc._channel import _InactiveRpcError
from pyhelm.chartbuilder import ChartBuilder
from pyhelm.tiller import Tiller
from onaptests.steps.base import BaseStep, YamlTemplateBaseStep
from onaptests.utils.simulators import get_local_dir
from onaptests.configuration import settings
from onaptests.utils.exceptions import  (
    TestConfigurationException, EnvironmentPreparationException,
    EnvironmentCleanupException)



class HelmChartStep(BaseStep):
    """Basic operations on a docker container."""

    def __init__(self,
                 cleanup: bool = False,
                 config_name: str = None,
                 namespace: str = 'default',
                 helm_repo_type: str = None,
                 release_name: str = None,
                 url: str = None) -> None:
        """Setup Helm chart configs, Tiller, and release name and path.

        Initialization example:
        simulator = HelmChartStep(
            cleanup=True,
            namespace="simulators"
            config_name="helm_chart_config.yaml",
            helm_repo_type="local",
            release_name="simulator")

        Arguments:
            cleanup (bool):
                determines if cleanup action should be called.
                Defaults to False.
            config_name (str):
                name of the config file that determines Helm chart info.
                Defaults to None.
            namespace (str):
                haelm chart destination namespace.
                Defaults to 'default'.
            helm_repo_type (str):
                remote or local. Defaults to None.
            release_name (str):
                name of the chart folder and the sname of chart installation.
                Defaults to None.
            release_name (str): remote's repo url if applicable.
                Defaults to None.

        """
        if not (config_name and release_name and helm_repo_type):
            msg = "Provide chart YAML config filename, release_name, repo type."
            raise TestConfigurationException(msg)

        super().__init__(cleanup=cleanup)

        self.release_name: str = release_name
        self.tiller = Tiller(settings.TILLER_HOST)

        try:
            template_obj = HelmYamlConfigTemplateStep(helm_repo_type=helm_repo_type,
                                                      filename=config_name,
                                                      release_name=release_name,
                                                      url=url)
            template_obj.execute()

            chart_info = template_obj.yaml_template

        except FileNotFoundError as err:
            msg = f"The Helm chart or config {self.release_name} does not exist."
            raise TestConfigurationException(msg) from err

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


class HelmYamlConfigTemplateStep(YamlTemplateBaseStep):
    """Read YAML config for Helm charts."""

    def __init__(self,  # pylint: disable=R0913
                 cleanup: bool = False,
                 helm_repo_type: str = "local",
                 filename: str = None,
                 release_name: str = None,
                 url: str = None):
        """Initialize step.

        Arguments:
            cleanup (bool):
                determines if cleanup action should be called.
                Defaults to False.
            repo_type (str):
                where to take charts from. So far only local.
                Defaults to local.
            filename (str): configuration file name. Defaults to None.
            release_name (str): release (repo) name. Defaults to None.
            url (str): remote Helm chart's repo. Defaults to None.
        """
        super().__init__(cleanup=cleanup)

        if not filename:
            raise TestConfigurationException("Provide .yaml config filename.")

        if helm_repo_type == "remote" and not (url and release_name):
            msg = "Provide name and url to the remote repo."
            raise TestConfigurationException(msg)

        if helm_repo_type == "local" and not release_name:
            raise TestConfigurationException("Local repo should have a name.")

        self._helm_repo_type: str = helm_repo_type
        self._path: Path = get_local_dir() / filename
        self._yaml_template: dict = None
        self._url: str = url
        self._release_name = release_name

    @property
    def description(self) -> str:
        """Step description."""
        return "Read YAML template configuration file."

    @property
    def component(self) -> str:
        """Component name."""
        return "Environment"

    @property
    def yaml_template(self) -> Dict:
        return self._yaml_template

    @yaml_template.setter
    def yaml_template(self, value) -> None:
        self._yaml_template = value

    def execute(self) -> None:
        """Read a config YAML file."""
        with open(self._path, "r") as ymlfile:
            self._yaml_template = yaml.safe_load(ymlfile)

        self._yaml_template["name"] = self._release_name

        if self._helm_repo_type == "local":
            self._yaml_template["source"]["type"] = "directory"
            self._yaml_template["source"]["location"] = get_local_dir() / self._release_name
        elif self._helm_repo_type == "remote":
            self._yaml_template["source"]["type"] = "repo"
            self._yaml_template["source"]["location"] = self._url
        else:
            raise NotImplementedError("Only local and remote repos supported.")
