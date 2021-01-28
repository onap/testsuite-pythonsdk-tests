"""Basic container commands to Docker."""
import yaml
from avionix import ChartBuilder, ChartDependency, ChartInfo
from avionix.errors import HelmError
from onaptests.steps.base import BaseStep
from onaptests.utils.simulators import get_local_dir
from onaptests.utils.exceptions import  (
    EnvironmentPreparationException,
    EnvironmentCleanupException)



class HelmChartStep(BaseStep):
    """Basic operations on a docker container."""

    def __init__(self,
                 cleanup: bool = False,
                 chart_info_file: str = None) -> None:
        """Setup Helm chart details.

        Arguments:
            cleanup (bool): cleanup after execution. Defaults to False.
            chart_info_file (str): description file of a chart. Default to None.
        """
        chart_info = None
        dependencies = []

        super().__init__(cleanup=cleanup)

        chart_info_path = get_local_dir() / chart_info_file

        try:
            with open(chart_info_path, 'r') as stream:
                chart_info = yaml.safe_load(stream)
        except IOError as err:
            msg = f"{chart_info_file} not found."
            raise EnvironmentPreparationException(msg) from err


        try:
            for dependency in chart_info["dependencies"]:
                dep = ChartDependency(
                    name=dependency["name"],
                    version=dependency["version"],
                    repository=dependency["repository"],
                    local_repo_name=dependency["local_repo_name"],
                    values=dependency["values"])
                dependencies.append(dep)

            self.builder = ChartBuilder(
                    chart_info=ChartInfo(
                        api_version=chart_info["api_version"],
                        name=chart_info["chart_name"],
                        version=chart_info["version"],  # SemVer 2 version
                        app_version=chart_info["app_version"],
                        dependencies=dependencies
                    ),
                    kubernetes_objects=[],
                    keep_chart=False
                )
        except KeyError as err:
            msg = f"{chart_info_file} does not contain required keys."
            raise EnvironmentPreparationException(msg) from err

    @property
    def description(self) -> str:
        """Step description."""
        return "Execute Helm charts."

    @property
    def component(self) -> str:
        """Component name."""
        return "Environment"

    @BaseStep.store_state
    def execute(self) -> None:
        """Install helm release."""
        super().execute()
        try:
            self.builder.install_chart({"dependency-update": None})
        except HelmError as err:
            msg = "Error during helm release installation."
            raise EnvironmentPreparationException(msg) from err


    def cleanup(self) -> None:
        """Uninstall helm release."""
        try:
            self.builder.uninstall_chart()
        except HelmError as err:
            msg = "Error during helm release deletion."
            raise EnvironmentCleanupException(msg) from err
        super().cleanup()
