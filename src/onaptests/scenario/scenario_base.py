import logging

from onapsdk.configuration import settings
from xtesting.core import testcase


class ScenarioBase(testcase.TestCase):
    """Scenario base class."""

    __logger = logging.getLogger()

    def __init__(self, case_name, **kwargs):
        """Init base scenario."""
        if "case_name" not in kwargs:
            kwargs["case_name"] = case_name
        self.__logger.info("Global Configuration:")
        for val in settings._settings:
            print(f"{val}: {settings._settings[val]}")
        super().__init__(**kwargs)
        self.__logger.debug("%s init started", kwargs["case_name"])
