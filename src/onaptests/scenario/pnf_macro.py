"""Instantiate service with PNF using SO macro flow."""
from onapsdk.configuration import settings
from yaml import SafeLoader, load

from onaptests.scenario.scenario_base import BaseStep, ScenarioBase, YamlTemplateBaseScenarioStep
from onaptests.steps.instantiate.pnf_register_ves import \
    SendPnfRegisterVesEvent
from onaptests.steps.instantiate.service_macro import \
    YamlTemplateServiceMacroInstantiateStep
from onaptests.steps.onboard.cds import CbaEnrichStep
from onaptests.steps.simulator.pnf_simulator_cnf.pnf_register import \
    PnfSimulatorCnfRegisterStep


class PnfMacroScenarioStep(YamlTemplateBaseScenarioStep):
    """Step created to run scenarion and generate report."""

    def __init__(self):
        """Initialize step.

        Substeps:
            - YamlTemplateServiceAlaCarteInstantiateStep.
        """
        super().__init__(cleanup=BaseStep.HAS_NO_CLEANUP)
        self._yaml_template: dict = None
        if settings.USE_SIMULATOR:
            self.add_step(PnfSimulatorCnfRegisterStep())
        else:
            self.add_step(SendPnfRegisterVesEvent())
        self.add_step(CbaEnrichStep())
        self.add_step(YamlTemplateServiceMacroInstantiateStep())

    @property
    def description(self) -> str:
        """Step description.

        Used for reports

        Returns:
            str: Step description

        """
        return "PNF macro scenario step"

    @property
    def component(self) -> str:
        """Component name.

        Name of component which step is related with.
            Most is the name of ONAP component.

        Returns:
            str: Component name

        """
        return "TEST"

    @property
    def yaml_template(self) -> dict:
        """YAML template abstract property.

        Every YAML template step need to implement that property.

        Returns:
            dict: YAML template

        """
        if not self._yaml_template:
            with open(settings.SERVICE_YAML_TEMPLATE, "r") as yaml_template:
                self._yaml_template: dict = load(yaml_template, SafeLoader)
        return self._yaml_template

    @property
    def model_yaml_template(self) -> dict:
        return {}

    @property
    def service_instance_name(self) -> str:
        """Service instance name.

        Returns:
            str: Service instance name

        """
        return settings.SERVICE_INSTANCE_NAME


class PnfMacro(ScenarioBase):
    """Run PNF simulator and onboard then instantiate a service with PNF."""

    def __init__(self, **kwargs):
        """Init Basic Network use case."""
        super().__init__('pnf_macro', **kwargs)
        self.test = PnfMacroScenarioStep()
