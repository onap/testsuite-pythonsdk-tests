"""MSB k8s plugin module."""
from onapsdk.configuration import settings
from onapsdk.k8s import Definition, Profile

from onaptests.steps.base import BaseStep
from onaptests.steps.cloud.cloud_region_create import CloudRegionCreateStep
from onaptests.steps.cloud.k8s_connectivity_info_create import K8SConnectivityInfoStep


class CreateDefinitionStep(BaseStep):
    """Create definition step initialization."""

    def __init__(self) -> None:
        """Initialize step.

        Substeps:
            - CloudRegionCreateStep,
            - K8SConnectivityInfoStep.
        """
        super().__init__(cleanup=False)
        self.add_step(CloudRegionCreateStep())
        self.add_step(K8SConnectivityInfoStep())
        self.definition: Definition = None

    @property
    def description(self) -> str:
        """Step description."""
        return "Create K8S definition."

    @property
    def component(self) -> str:
        """Component name."""
        return "K8S plugin"

    @BaseStep.store_state
    def execute(self) -> None:
        """Create definition."""
        super().execute()
        with open(settings.MSB_K8S_DEFINITION_ATRIFACT_FILE_PATH, "rb") as definition_file:
            self.definition = Definition.create(rb_name=settings.MSB_K8S_RB_NAME,
                                                rb_version=settings.MSB_K8S_RB_VERSION)
            self.definition.upload_artifact(definition_file.read())


class CreateProfileStep(BaseStep):
    """Create profile step."""

    def __init__(self) -> None:
        """Initialize step.

        Substeps:
            - CreateDefinitionStep.
        """
        super().__init__(cleanup=False)
        self.add_step(CreateDefinitionStep())
        self.profile: Profile = None

    @property
    def description(self) -> str:
        """Step description."""
        return "Create K8S profile."

    @property
    def component(self) -> str:
        """Component name."""
        return "K8S plugin"

    @BaseStep.store_state
    def execute(self) -> None:
        """Create profile."""
        super().execute()
        definition: Definition = Definition.get_definition_by_name_version(
            rb_name=settings.MSB_K8S_RB_NAME,
            rb_version=settings.MSB_K8S_RB_VERSION)
        with open(settings.MSB_K8S_PROFILE_ARTIFACT_FILE_PATH, "rb") as profile_file:
            self.profile = definition.create_profile(
                profile_name=settings.MSB_K8S_PROFILE_NAME,
                namespace=settings.K8S_ADDITIONAL_RESOURCES_NAMESPACE,
                kubernetes_version=settings.K8S_VERSION)
            self.profile.upload_artifact(profile_file.read())
