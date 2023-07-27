"""Basic Clamp test case."""
from onaptests.scenario.scenario_base import ScenarioBase
from onaptests.steps.loop.clamp import ClampStep


class BasicClamp(ScenarioBase):
    """Onboard, update a model with a loop, design the loop and deploy it."""

    def __init__(self, **kwargs):
        """Init Basic Clamp, onboard a VM, design and deploy a loop with CLAMP."""
        super().__init__('basic_clamp', **kwargs)
        self.test = ClampStep()
