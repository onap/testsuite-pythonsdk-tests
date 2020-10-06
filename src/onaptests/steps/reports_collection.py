from typing import Dict
from queue import SimpleQueue


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
            print(element)
            print(type(element))
            report.update(element)
        return report
