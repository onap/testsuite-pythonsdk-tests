import sys
from dataclasses import dataclass
from enum import Enum
from typing import List
from jinja2 import Environment, FileSystemLoader, select_autoescape
from onapsdk.configuration import settings
from onapsdk.exceptions import SettingsError

class ReportStepStatus(Enum):
    """Enum which stores steps execution statuses."""
    PASS = "PASS"
    FAIL = "FAIL"


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
        return sum((1 for step_report in self.report if \
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
            loader=FileSystemLoader(sys.path[-1] + '/onaptests/templates/reporting'))

        jinja_env.get_template('reporting.html.j2').stream(
            report=self,
            usecase=usecase,
            details=details,
            components=components,
            log_path="./pythonsdk.debug.log").dump(
            settings.REPORTING_FILE_PATH)
