from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
from typing import List
from jinja2 import Environment, FileSystemLoader, select_autoescape
from onapsdk.configuration import settings
from onapsdk.exceptions import SettingsError
from onaptests.utils.resources import get_resource_location


class ReportStepStatus(Enum):
    """Enum which stores steps execution statuses."""
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_EXECUTED = "NOT EXECUTED"


@dataclass
class Report:
    """Step execution report."""
    step_description: str
    step_execution_status: ReportStepStatus
    step_execution_duration: float


class ReportsCollection:
    """Collection to store steps execution statuses."""

    def __init__(self) -> None:
        """Initialize collection."""
        self._collection: list = []

    def put(self, item: Report) -> None:
        """Put execution status dictionary.

        Args:
            item (Report): Step report

        """
        self._collection.insert(0, item)

    @property
    def report(self) -> List[Report]:
        """Get report.

        Build a dictionary with execution statuses.

        Returns:
            List[str, str]: Steps name with status dictionary

        """
        return self._collection

    @property
    def failed_steps_num(self) -> int:
        """Number of failed steps in report.

        Returns:
            int: How many steps failed

        """
        return sum((1 for step_report in self.report if
                    step_report.step_execution_status == ReportStepStatus.FAIL))

    def generate_report(self) -> None:
        usecase = settings.SERVICE_NAME
        try:
            details = settings.SERVICE_DETAILS
        except (KeyError, AttributeError, SettingsError):
            details = ""

        try:
            components = settings.SERVICE_COMPONENTS
        except (KeyError, AttributeError, SettingsError):
            components = ""

        jinja_env = Environment(
            autoescape=select_autoescape(['html']),
            loader=FileSystemLoader(get_resource_location('templates/reporting')))

        jinja_env.get_template('reporting.html.j2').stream(
            report=self,
            usecase=usecase,
            details=details,
            components=components,
            log_path="./pythonsdk.debug.log").dump(
                str(Path(settings.REPORTING_FILE_DIRECTORY).joinpath(settings.HTML_REPORTING_FILE_NAME)))

        report_dict = {
            'usecase': usecase,
            'details': details,
            'components': components,
            'steps': [
                {
                    'description': step_report.step_description,
                    'status': step_report.step_execution_status.value,
                    'duration': step_report.step_execution_duration
                }
                for step_report in self.report
            ]
        }
        report_dict['steps'].sort(key=lambda step: int(''.join(filter(str.isdigit, step['description']))))
        with (Path(settings.REPORTING_FILE_DIRECTORY).joinpath(settings.JSON_REPORTING_FILE_NAME)).open('w') as file:
            json.dump(report_dict, file, indent=4)
        return report_dict
