#!/usr/bin/env python
"""Basic Onboard test case."""
from onapsdk.configuration import settings
from yaml import SafeLoader, load

from onaptests.scenario.scenario_base import (BaseStep, ScenarioBase,
                                              YamlTemplateBaseScenarioStep)
from onaptests.steps.onboard.service import (VerifyServiceDistributionStep,
                                             YamlTemplateServiceOnboardStep)


class BasicSdcOnboardStep(YamlTemplateBaseScenarioStep):
    """Main basic onboard scenario step."""

    def __init__(self):
        """Initialize step.

        Substeps:
            - YamlTemplateServiceOnboardStep
            - VerifyServiceDistributionStep (optional).
        """
        super().__init__(cleanup=BaseStep.HAS_NO_CLEANUP)
        self._yaml_template: dict = None
        self.add_step(YamlTemplateServiceOnboardStep())
        if settings.VERIFY_DISTRIBUTION:
            self.add_step(VerifyServiceDistributionStep())

    @property
    def description(self) -> str:
        """Step description.

        Used for reports

        Returns:
            str: Step description

        """
        return "Basic SDC Onboard scenario step"

    @property
    def component(self) -> str:
        """Component name.

        Name of component which step is related with.
            Most is the name of ONAP component.

        Returns:
            str: Component name

        """
        return "SDC"

    @property
    def yaml_template(self) -> dict:
        """YAML template abstract property.

        Every YAML template step need to implement that property.

        Returns:
            dict: YAML template

        """
        if not self._yaml_template:
            with open(settings.SERVICE_YAML_TEMPLATE, "r", encoding="utf-8") as yaml_template:
                self._yaml_template: dict = load(yaml_template, SafeLoader)
        return self._yaml_template

    @property
    def model_yaml_template(self) -> dict:
        return {}


class BasicOnboard(ScenarioBase):
    """Onboard a simple VM with ONAP."""

    def __init__(self, **kwargs):
        """Init BasicOnboard."""
        # import basic_onboard_settings needed
        super().__init__('basic_onboard', **kwargs)
        self.test = BasicSdcOnboardStep()
