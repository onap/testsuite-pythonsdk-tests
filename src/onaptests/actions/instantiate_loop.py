#!/usr/bin/python
# http://www.apache.org/licenses/LICENSE-2.0
"""Instantiation class."""
import logging

from onapsdk.clamp.clamp_element import Clamp
from onapsdk.clamp.loop_instance import LoopInstance
from onapsdk.sdc.service import Service


class InstantiateLoop():
    """class instantiating a closed loop in clamp."""

    def __init__(self, template: str, loop_name: str, operational_policies: list):
        self.template=template,          
        self.loop_name=loop_name,
        self.operational_policies=operational_policies
        self.set_logger()
    
    def set_logger(self):
        """Set logger."""
        self.logger = logging.getLogger("")
        handler = logging.StreamHandler()
        fh_formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(lineno)d:%(filename)s(%(process)d) - %(message)s')
        handler.setFormatter(fh_formatter)
        self.logger.addHandler(handler)

    def add_policies(self, loop: LoopInstance) -> None:
        """add necessary wanted operational policies."""
        
        for policy in self.operational_policies:
            self.logger.info("******** ADD OPERATIONAL POLICY %s *******", policy["name"])
            added = loop.add_operational_policy(policy_type=policy["policy_type"],
                                                policy_version=policy["policy_version"])

    def configure_policies(self, loop: LoopInstance) -> None:
        """Configure all policies."""
        self.logger.info("******** UPDATE MICROSERVICE POLICY *******")
        loop._update_loop_details()
        loop.update_microservice_policy()
        for policy in self.operational_policies:
            #loop.add_op_policy_config(loop.LoopInstance.__dict__[policy["config_function"]])
            #possible configurations for the moment
            if policy["name"] == "MinMax":
                loop.add_op_policy_config(loop.add_minmax_config)
            if policy["name"] == "Drools":
                loop.add_op_policy_config(loop.add_drools_conf)
            if policy["name"] == "FrequencyLimiter":
                loop.add_op_policy_config(loop.add_frequency_limiter)
        self.logger.info("Policies are well configured")

    def deploy(self, loop: LoopInstance) -> None:
        """Deploy closed loop."""
        self.logger.info("******** SUBMIT POLICIES TO PE *******")
        submit = loop.act_on_loop_policy(action="submit")
        self.logger.info("******** CHECK POLICIES SUBMITION *******")
        if submit :
            self.logger.info("Policies successfully submited to PE")
        else:
            self.logger.error("An error occured while submitting the loop instance")
            exit(1)
        self.logger.info("******** DEPLOY LOOP INSTANCE *******")
        deploy = loop.deploy_microservice_to_dcae()
        if deploy:
            self.logger.info("Loop instance %s successfully deployed on DCAE !!", self.loop_name)
        else:
            self.logger.error("An error occured while deploying the loop instance")
            exit(1)

    def instantiate_loop(self):
        # temp solution 
        self.loop_name= ''.join(self.loop_name)
        self.template =''.join(self.template)
        #end
        loop = LoopInstance(template=self.template,
                            name=self.loop_name,
                            details={})
        details = loop.create()
        if details:
            self.logger.info("Loop instance %s successfully created !!", self.loop_name)
        else:
            self.logger.error("An error occured while creating the loop instance")

        self.add_policies(loop=loop)
        self.configure_policies(loop=loop)
        self.deploy(loop=loop)

        loop.details = loop._update_loop_details()
        return loop
