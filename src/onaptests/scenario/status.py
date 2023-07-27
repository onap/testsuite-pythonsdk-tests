from onaptests.scenario.scenario_base import ScenarioBase
from onaptests.steps.cloud.check_status import CheckNamespaceStatusStep


class Status(ScenarioBase):
    """Retrieve status of Kubernetes resources in the nemaspace."""

    def __init__(self, **kwargs):
        """Init the testcase."""
        super().__init__('status', **kwargs)
        self.test = CheckNamespaceStatusStep()
