#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
"""Clamp Scenario class."""
from yaml import load
import random
import string
import time

from onapsdk.clamp.clamp_element import Clamp
from onapsdk.sdc.service import Service

import onaptests.utils.exceptions as onap_test_exceptions
from onapsdk.configuration import settings
from onaptests.steps.onboard.clamp import OnboardClampStep
from onaptests.steps.loop.instantiate_loop import InstantiateLoop

from ..base import YamlTemplateBaseStep


class ClampStep(YamlTemplateBaseStep):
    """class defining the different CLAMP scenarios."""

    count: int = 0

    def __init__(self, cleanup=False):
        super().__init__(cleanup=cleanup)
        self._yaml_template: dict = None
        self.add_step(OnboardClampStep(cleanup=cleanup))
        Clamp()
        self.loop_instance = None

    @property
    def description(self) -> str:
        """Step description."""
        return "Retrieve TCA, Policy then create a loop"

    @property
    def component(self) -> str:
        """Component name."""
        return "CLAMP"

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


    def check(self, operational_policies: list, is_template: bool = False) -> str:
        """Check CLAMP requirements to create a loop."""
        self._logger.info("Check operational policy")
        for policy in operational_policies:
            exist = Clamp.check_policies(policy_name=policy["name"],
                                         req_policies=30)# 30 required policy
            self._logger.info("Operational policy found.")
            if not exist:
                raise ValueError("Couldn't load the policy %s", policy)
        # retrieve the service..based on service name
        service: Service = Service(self.service_name)
        if is_template:
            loop_template = Clamp.check_loop_template(service=service)
            self._logger.info("Loop template checked.")
            return loop_template

    def instantiate_clamp(self, loop_template: str, loop_name: str, operational_policies: list):
        """Instantite a closed loopin CLAMP."""
        letters = string.ascii_letters
        loop_name_random = loop_name.join(
            random.choice(letters) for i in range(6))
        loop = InstantiateLoop(template=loop_template,
                               loop_name=loop_name_random,
                               operational_policies=operational_policies)
        return loop.instantiate_loop()

    def loop_counter(self, action: str) -> None:
        """ Count number of loop instances."""
        if  action == "plus":
            self.count += 1
        if  action == "minus":
            self.count -= 1

    @YamlTemplateBaseStep.store_state
    def execute(self):
        super().execute() # TODO work only the 1st time, not if already onboarded

        # Before instantiating, be sure that the service has been distributed
        service = Service(self.service_name)
        self._logger.info("******** Check Service Distribution *******")
        distribution_completed = False
        nb_try = 0
        nb_try_max = 10
        while distribution_completed is False and nb_try < nb_try_max:
            distribution_completed = service.distributed
            if distribution_completed is True:
                self._logger.info(
                "Service Distribution for %s is sucessfully finished",
                service.name)
                break
            self._logger.info(
                "Service Distribution for %s ongoing, Wait for 60 s",
                service.name)
            time.sleep(60)
            nb_try += 1

        if distribution_completed is False:
            self._logger.error(
                "Service Distribution for %s failed !!",service.name)
            raise onap_test_exceptions.ServiceDistributionException

        # time to wait for template load in CLAMP
        self._logger.info("Wait a little bit to give a chance to the distribution")
        time.sleep(settings.CLAMP_DISTRIBUTION_TIMER)
        # Test 1
        operational_policies = settings.OPERATIONAL_POLICIES
        loop_template = self.check(operational_policies, True)
        # Test 2
        loop_name = "instance_" + self.service_name + str(self.count)
        self.loop_counter(action="plus")
        self.loop_instance = self.instantiate_clamp(
            loop_template=loop_template,
            loop_name=loop_name,
            operational_policies=operational_policies)

    @YamlTemplateBaseStep.store_state(cleanup=True)
    def cleanup(self) -> None:
        """Cleanup Service.

        Raises:
            Exception: Clamp cleaning failed

        """
        self.loop_counter(action="minus")
        self.loop_instance.undeploy_microservice_from_dcae()
        self.loop_instance.delete()
        super().cleanup()
