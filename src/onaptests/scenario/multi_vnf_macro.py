"""Instantiate basic vm using SO macro flow."""
from onapsdk.configuration import settings
from yaml import SafeLoader, load

from onaptests.scenario.scenario_base import (BaseStep, ScenarioBase,
                                              YamlTemplateBaseScenarioStep)
from onaptests.steps.instantiate.service_macro import \
    YamlTemplateServiceMacroInstantiateStep
from onaptests.steps.onboard.cds import CbaPublishStep


class MultiVnfUbuntuMacroStep(YamlTemplateBaseScenarioStep):
    """Main step for multi vnf instantiation with macro method."""

    def __init__(self):
        """Initialize step.

        Substeps:
            - CbaPublishStep
            - YamlTemplateServiceAlaCarteInstantiateStep.
        """
        super().__init__(cleanup=BaseStep.HAS_NO_CLEANUP)
        self._yaml_template: dict = None
        self._model_yaml_template: dict = None
        self.add_step(CbaPublishStep())
        self.add_step(YamlTemplateServiceMacroInstantiateStep())

    @property
    def description(self) -> str:
        """Step description.

        Used for reports

        Returns:
            str: Step description

        """
        return "Multi VNF Ubuntu macro scenario step"

    @property
    def component(self) -> str:
        """Component name.

        Name of component which step is related with.
            Most is the name of ONAP component.

        Returns:
            str: Component name

        """
        return "PythonSDK-tests"

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
        if not self._model_yaml_template:
            with open(settings.MODEL_YAML_TEMPLATE, "r", encoding="utf-8") as model_yaml_template:
                self._model_yaml_template: dict = load(model_yaml_template, SafeLoader)
        return self._model_yaml_template

    @property
    def service_instance_name(self) -> str:
        """Service instance name.

        Returns:
            str: Service instance name

        """
        return settings.SERVICE_INSTANCE_NAME


class MultiVnfUbuntuMacro(ScenarioBase):
    """Instantiate a basic vm macro."""

    def __init__(self, **kwargs):
        """Init Basic Macro use case."""
        super().__init__('nso_ubuntu_macro', **kwargs)
        self.test = MultiVnfUbuntuMacroStep()
