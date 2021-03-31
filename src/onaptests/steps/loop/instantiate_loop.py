#!/usr/bin/python
# http://www.apache.org/licenses/LICENSE-2.0
"""Instantiation class."""
import logging
import logging.config

from onapsdk.clamp.loop_instance import LoopInstance
from onapsdk.configuration import settings


class InstantiateLoop():
    """class instantiating a closed loop in clamp."""

    def __init__(self, template: str, loop_name: str, operational_policies: list):
        self.template=template
        self.loop_name=loop_name
        self.operational_policies=operational_policies

        self._logger: logging.Logger = logging.getLogger("")
        logging.config.dictConfig(settings.LOG_CONFIG)

    def add_policies(self, loop: LoopInstance) -> None:
        """add necessary wanted operational policies."""
        for policy in self.operational_policies:
            self._logger.info("******** ADD OPERATIONAL POLICY %s *******", policy["name"])
            added = loop.add_operational_policy(policy_type=policy["policy_type"],
                                                policy_version=policy["policy_version"])
            if not added:
                self._logger.error("an error occured while adding an operational policy")
            self._logger.info("ADD OPERATION SUCCESSFULY DONE")


    def configure_policies(self, loop: LoopInstance) -> None:
        """Configure all policies."""
        self._logger.info("******** UPDATE MICROSERVICE POLICY *******")
        loop._update_loop_details()
        loop.update_microservice_policy()
        self._logger.info("******** UPDATE OPERATIONAL POLICIES CONFIG *******")
        for policy in self.operational_policies:
            #loop.add_op_policy_config(loop.LoopInstance.__dict__[policy["config_function"]])
            #possible configurations for the moment
            if policy["name"] == "MinMax":
                loop.add_op_policy_config(loop.add_minmax_config)
            if policy["name"] == "Drools":
                loop.add_op_policy_config(loop.add_drools_conf)
            if policy["name"] == "FrequencyLimiter":
                loop.add_op_policy_config(loop.add_frequency_limiter)
        self._logger.info("Policies are well configured")

    def deploy(self, loop: LoopInstance) -> None:
        """Deploy closed loop."""
        self._logger.info("******** SUBMIT POLICIES TO PE *******")
        submit = loop.act_on_loop_policy(loop.submit)
        self._logger.info("******** CHECK POLICIES SUBMITION *******")
        if submit :
            self._logger.info("Policies successfully submited to PE")

        else:
            self._logger.error("An error occured while submitting the loop instance")
            exit(1)
        self._logger.info("******** DEPLOY LOOP INSTANCE *******")
        deploy = loop.deploy_microservice_to_dcae()
        if deploy:
            self._logger.info("Loop instance %s successfully deployed on DCAE !!", self.loop_name)
        else:
            self._logger.error("An error occured while deploying the loop instance")
            exit(1)

    def instantiate_loop(self):
        """Instantiate the control loop."""
        loop = LoopInstance(template=self.template,
                            name=self.loop_name,
                            details={})
        details = loop.create()
        if details:
            self._logger.info("Loop instance %s successfully created !!", self.loop_name)
        else:
            self._logger.error("An error occured while creating the loop instance")

        self.add_policies(loop=loop)
        self.configure_policies(loop=loop)
        self.deploy(loop=loop)

        loop.details = loop._update_loop_details()
        return loop
