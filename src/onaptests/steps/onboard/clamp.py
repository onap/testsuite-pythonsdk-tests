#!/usr/bin/python
# http://www.apache.org/licenses/LICENSE-2.0
"""Clamp Onboard service class."""
from yaml import load
from onapsdk.sdc.service import Service
from onapsdk.sdc.vf import Vf

from onapsdk.configuration import settings

from ..base import YamlTemplateBaseStep
from .service import YamlTemplateVfOnboardStep

class OnboardClampStep(YamlTemplateBaseStep):
    """Onboard class to create CLAMP templates."""

    def __init__(self, cleanup=False):
        """Initialize Clamp Onboard object."""
        super().__init__(cleanup=cleanup)
        self._yaml_template: dict = None
        self.add_step(YamlTemplateVfOnboardStep(cleanup=cleanup))
        # if "service_name" in kwargs:
        #     self.service_name = kwargs['service_name']
        # else:
        #     raise ValueError("Service Name to define")
        # self.vf_list = []
        # self.vsp_list = []
        # self.set_logger()

    @property
    def description(self) -> str:
        """Step description."""
        return "Onboard service in SDC including a TCA blueprint for CLAMP."

    @property
    def component(self) -> str:
        """Component name."""
        return "SDC"

    @property
    def yaml_template(self) -> dict:
        """Step YAML template.

        Load from file if it's a root step, get from parent otherwise.

        Returns:
            dict: Step YAML template

        """
        if self.is_root:
            if not self._yaml_template:
                with open(settings.SERVICE_YAML_TEMPLATE, "r") as yaml_template:
                    self._yaml_template: dict = load(yaml_template)
            return self._yaml_template
        return self.parent.yaml_template

    @property
    def model_yaml_template(self) -> dict:
        return {}

    @property
    def service_name(self) -> str:
        """Service name.

        Get from YAML template if it's a root step, get from parent otherwise.

        Returns:
            str: Service name

        """
        if self.is_root:
            return next(iter(self.yaml_template.keys()))
        else:
            return self.parent.service_name

    @YamlTemplateBaseStep.store_state
    def execute(self):
        """Onboard service."""
        super().execute()
        # retrieve the Vf
        vf = None
        for sdc_vf in Vf.get_all():
            if sdc_vf.name == settings.VF_NAME:
                vf = sdc_vf
        self._logger.debug("Vf retrieved %s", vf)

        service: Service = Service(name=self.service_name,
                                   resources=[vf])
        service.create()
        self._logger.info(" Service %s created", service)

        if not service.distributed:
            service.add_resource(vf)

            # we add the artifact to the first VNF
            self._logger.info("Try to add blueprint to %s", vf.name)
            payload_file = open(settings.CONFIGURATION_PATH + 'tca-microservice.yaml', 'rb')
            data = payload_file.read()
            self._logger.info("DCAE INVENTORY BLUEPRINT file retrieved")
            service.add_artifact_to_vf(vnf_name=vf.name,
                                       artifact_type="DCAE_INVENTORY_BLUEPRINT",
                                       artifact_name="tca-microservice.yaml",
                                       artifact=data)
            payload_file.close()
            service.checkin()
            service.onboard()
            self._logger.info("DCAE INVENTORY BLUEPRINT ADDED")
