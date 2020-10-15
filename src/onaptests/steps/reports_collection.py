import sys
from typing import Dict
from jinja2 import Environment, FileSystemLoader, select_autoescape
from onapsdk.configuration import settings

class ReportsCollection:
    """Collection to store steps execution statuses."""

    def __init__(self) -> None:
        """Initialize collection."""
        self._collection: list = []

    def put(self, item: Dict[str, str]) -> None:
        """Put execution status dictionary.

        Args:
            item (Dict[str, str]): Step name with status dictionary

        """
        self._collection.append(item)

    @property
    def report(self) -> Dict[str, str]:
        """Get report.

        Build a dictionary with execution statuses.

        Returns:
            Dict[str, str]: Steps name with status dictionary

        """
        report: Dict[str, str] = {}
        for element in self._collection[::-1]:
            report.update(element)
        return report

    def generate_report(self) -> None:
        step_list = self.report
        failing_steps = {}
        for step,status in step_list.items():
            if 'FAIL' in status:
                failing_steps[step] = status
        usecase = settings.SERVICE_NAME
        try:
            details = settings.SERVICE_DETAILS
        except NameError:
            details = ""

        try:
            components = settings.SERVICE_COMPONENTS
        except NameError:
            components = ""

        jinja_env = Environment(
            autoescape=select_autoescape(['html']),
            loader=FileSystemLoader(sys.path[-1] + '/onaptests/templates/reporting'))

        jinja_env.get_template('reporting.html.j2').stream(
            failing_steps=failing_steps,
            steps=step_list,
            usecase=usecase,
            details=details,
            components=components,
            log_path="./pythonsdk.debug.log").dump(
            settings.REPORTING_FILE_PATH)
