"""MSB k8s instantiation module."""
import time

from onapsdk.configuration import settings
from onapsdk.exceptions import APIError
from onapsdk.msb.k8s import Instance

from onaptests.steps.base import BaseStep
from onaptests.steps.onboard.msb_k8s import CreateProfileStep


class InstancesCleanup(BaseStep):
    """Delete old instances which were not cleaned up properly."""

    @property
    def description(self) -> str:
        """Step description."""
        return ("Delete old instances which were created using same MSB_K8S_RESOURCE_NAME_PREFIX"
                " and were not cleaned up.")

    @property
    def component(self) -> str:
        """Component name."""
        return "K8S plugin"

    @BaseStep.store_state
    def execute(self) -> None:
        """Create instance using MSB K8S plugin."""
        super().execute()
        self._logger.debug("Delete all instances which are created using definition with same prefix ")
        any_deleted: bool = False
        try:
            for instance in Instance.get_all():
                if instance.request.profile_name.startswith(settings.MSB_K8S_RESOURCE_NAME_PREFIX):
                    self._logger.debug("Delete %s instance", instance.instance_id)
                    instance.delete()
                    any_deleted = True
            if any_deleted:
                time.sleep(settings.MSB_K8S_CLEANUP_WAIT_TIME)  # Give it some time to delete k8s resources (pods, services, deployments...)
        except APIError:
            self._logger.debug("There are no MSB K8S instances")


class CreateInstanceStep(BaseStep):
    """Create MSB k8s instance step."""

    def __init__(self, cleanup: bool = False) -> None:
        """Initialize step.

        Substeps:
            - CreateProfileStep.
        """
        super().__init__(cleanup=cleanup)
        self.add_step(InstancesCleanup())
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
                                        profile_name=settings.MSB_K8S_PROFILE_NAME,
                                        rb_name=settings.MSB_K8S_RB_NAME,
                                        rb_version=settings.MSB_K8S_RB_VERSION)

    @BaseStep.store_state(cleanup=True)
    def cleanup(self) -> None:
        """Delete instance."""
        if self.instance:
            self.instance.delete()
        return super().cleanup()
