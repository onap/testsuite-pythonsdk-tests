import logging

from onapsdk.configuration import settings
from onapsdk.exceptions import APIError
from onapsdk.sdnc import VfModulePreload
from onapsdk.sdnc.preload import PreloadInformation
from onapsdk.sdnc.services import Service

from onaptests.scenario.scenario_base import BaseScenarioStep
from onaptests.steps.base import BaseStep
from onaptests.utils.exceptions import OnapTestException


class BaseSdncStep(BaseStep):
    """Basic SDNC step."""

    def __init__(self, cleanup: bool = False):
        """Initialize step."""
        super().__init__(cleanup=cleanup)

    @property
    def component(self) -> str:
        """Component name.

        Name of component which step is related with.
            Most is the name of ONAP component.

        Returns:
            str: Component name

        """
        return "SDNC"


class ServiceCreateStep(BaseSdncStep):
    """Service creation step."""

    def __init__(self, service: Service = None):
        """Initialize step."""
        super().__init__(cleanup=settings.CLEANUP_FLAG)
        self.service = service

    @property
    def description(self) -> str:
        """Step description."""
        return "Create SDNC service."

    @BaseStep.store_state
    def execute(self) -> None:
        """Create service at SDNC."""
        super().execute()
        self._logger.info("Create new service instance in SDNC by GR-API")
        try:
            self.service = Service(
                service_instance_id=settings.SERVICE_ID,
                service_status=settings.SERVICE_STATUS,
                service_data=settings.SERVICE_DATA
            )
            self.service.create()
            self._logger.info("SDNC service is created.")
        except APIError as exc:
            if exc.response_status_code == 409:
                self._logger.warning("SDNC service already exists.")
            else:
                raise OnapTestException("SDNC service creation failed.") from exc

    @BaseStep.store_state(cleanup=True)
    def cleanup(self) -> None:
        """Cleanup Service."""
        if self.service is not None:
            self.service.delete()
            self._logger.info("SDNC service is deleted.")
        super().cleanup()


class UpdateSdncService(BaseSdncStep):
    """Service update step.

    The step needs in an existing SDNC service as a prerequisite.
    """

    def __init__(self):
        """Initialize step.

        Sub steps:
            - ServiceCreateStep.
        """
        super().__init__(cleanup=BaseStep.HAS_NO_CLEANUP)
        self.add_step(ServiceCreateStep())

    @property
    def description(self) -> str:
        """Step description.

        Used for reports

        Returns:
            str: Step description

        """
        return "Update SDNC service"

    @BaseSdncStep.store_state
    def execute(self) -> None:
        super().execute()
        self._logger.info("Get existing SDNC service instance and update it over GR-API")
        try:
            service = Service.get(settings.SERVICE_ID)
            service.service_status = settings.SERVICE_CHANGED_STATUS
            service.service_data = settings.SERVICE_CHANGED_DATA
            service.update()
            self._logger.info("SDNC service update is completed.")
        except APIError as exc:
            raise OnapTestException("SDNC service update is failed.") from exc


class UploadVfModulePreloadStep(BaseSdncStep):
    """Upload preload information for VfModule.

    Upload preload information for VfModule over GR-API.
    """

    def __init__(self):
        """Initialize step."""
        super().__init__(cleanup=BaseStep.HAS_NO_CLEANUP)

    @property
    def description(self) -> str:
        """Step description.

        Used for reports

        Returns:
            str: Step description

        """
        return "Upload Preload information for VfModule"

    @BaseSdncStep.store_state
    def execute(self) -> None:
        super().execute()
        self._logger.info("Upload VfModule preload information over GR-API")
        VfModulePreload.upload_vf_module_preload(
            {
                "vnf_name": settings.VNF_NAME,
                "vnf_type": settings.VNF_TYPE
            },
            settings.VF_MODULE_NAME,
            None
        )


class GetSdncPreloadStep(BaseSdncStep):
    """Get preload information from SDNC.

    Get preload information from SDNC over GR-API.
    """

    __logger = logging.getLogger(__name__)

    def __init__(self):
        """Initialize step.

        Sub steps:
            - UploadVfModulePreloadStep.
        """
        super().__init__(cleanup=BaseStep.HAS_NO_CLEANUP)
        self.add_step(UploadVfModulePreloadStep())

    @property
    def description(self) -> str:
        """Step description.

        Used for reports

        Returns:
            str: Step description

        """
        return "Get Preload information"

    @BaseSdncStep.store_state
    def execute(self) -> None:
        super().execute()
        self._logger.info("Get existing SDNC service instance and update it over GR-API")
        preloads = PreloadInformation.get_all()
        for preload_information in preloads:
            self.__logger.debug(preload_information)


class TestSdncStep(BaseScenarioStep):
    """Top level step for SDNC tests."""

    def __init__(self):
        """Initialize step.

        Sub steps:
            - UpdateSdncService.
        """
        super().__init__(cleanup=BaseStep.HAS_NO_CLEANUP)
        self.add_step(UpdateSdncService())
        self.add_step(GetSdncPreloadStep())

    @property
    def description(self) -> str:
        """Step description.

        Used for reports

        Returns:
            str: Step description

        """
        return "Test SDNC functionality scenario step"

    @property
    def component(self) -> str:
        """Component name.

        Name of component which step is related with.
            Most is the name of ONAP component.

        Returns:
            str: Component name

        """
        return "TEST"
