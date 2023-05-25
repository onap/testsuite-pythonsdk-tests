import logging

from onapsdk.sdnc.services import Service
from onapsdk.configuration import settings
from onapsdk.exceptions import APIError

from ..base import BaseStep


class ServiceCreateStep(BaseStep):
    """Service creation step."""

    def __init__(self, service: Service = None, cleanup: bool = False):
        """Initialize step."""
        super().__init__(cleanup=cleanup)
        self.service = service

    @property
    def description(self) -> str:
        """Step description."""
        return "Create SDNC service."

    @property
    def component(self) -> str:
        """Component name."""
        return "SDNC"

    @BaseStep.store_state
    def execute(self):
        """Create service at SDNC."""
        super().execute()
        try:
            self.service = Service(
                service_instance_id=settings.SERVICE_ID,
                service_status=settings.SERVICE_STATUS,
                service_data=settings.SERVICE_DATA
            )
            self.service.create()
            self._logger.info("SDNC service is created.")
        except APIError:
            self._logger.warning("SDNC service creation failed.")

    @BaseStep.store_state()
    def cleanup(self) -> None:
        """Cleanup Service."""
        if self.service is not None:
            self.service.delete()
            self._logger.info("SDNC service is deleted.")
        super().cleanup()


class BasicSdncStep(BaseStep):

    __logger = logging.getLogger()

    def __init__(self, cleanup=False):
        """Initialize step.

        Sub steps:
            - ServiceCreateStep.
        """
        super().__init__(cleanup=cleanup)
        self.add_step(ServiceCreateStep(cleanup=cleanup))

    @property
    def description(self) -> str:
        """Step description.

        Used for reports

        Returns:
            str: Step description

        """
        return "Basic SDNC scenario step"

    @property
    def component(self) -> str:
        """Component name.

        Name of component which step is related with.
            Most is the name of ONAP component.

        Returns:
            str: Component name

        """
        return "SDNC"

    def run(self):
        service: Service
        try:
            service = Service.get(settings.SERVICE_ID)
            self._logger.info("SDNC service availability is checked. "
                              "The service is available in SDNC.")
            service.service_status = settings.SERVICE_CHANGED_STATUS
            service.service_data = settings.SERVICE_CHANGED_DATA
            service.update()
            self._logger.info("SDNC service update is checked.")
        except APIError:
            self._logger.warning("SDNC service get/update is failed.")
