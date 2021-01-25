"""MSB k8s instantiation module."""
from onapsdk.configuration import settings
from onapsdk.msb.k8s import Instance

from onaptests.steps.base import BaseStep
from onaptests.steps.onboard.msb_k8s import CreateProfileStep


class CreateInstanceStep(BaseStep):
    """Create MSB k8s instance step."""

    def __init__(self, cleanup: bool = False) -> None:
        """Initialize step.

        Substeps:
            - CreateProfileStep.
        """
        super().__init__(cleanup=cleanup)
        self.add_step(CreateProfileStep(cleanup=cleanup))
        self.instance: Instance = None

    @property
    def description(self) -> str:
        """Step description."""
        return "Create K8S instance."

    @property
    def component(self) -> str:
        """Component name."""
        return "K8S plugin"

    @BaseStep.store_state
    def execute(self) -> None:
        """Create instance using MSB K8S plugin."""
        super().execute()
        self.instance = Instance.create(cloud_region_id=settings.CLOUD_REGION_ID,
                                        profile_name=settings.PNF_PROFILE_NAME,
                                        rb_name=settings.PNF_RB_NAME,
                                        rb_version=settings.PNF_RB_VERSION)

    def cleanup(self) -> None:
        """Delete instance."""
        if self.instance:
            self.instance.delete()
        return super().cleanup()
