#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
"""Scenario class."""
import os
import logging
import oyaml as yaml
from onapsdk.configuration import settings
from onapsdk.aai.business import Customer

class Common():
    """Mother common class."""

    def __init__(self):
        """Initialize scenario object."""
        super().__init__()
        self.set_logger()
        self.set_proxy(settings.SOCK_HTTP)

    def set_logger(self):
        """Set logger."""
        self.logger = logging.getLogger("")
        handler = logging.StreamHandler()
        fh_formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(lineno)d:%(filename)s(%(process)d) - %(message)s')
        handler.setFormatter(fh_formatter)
        self.logger.addHandler(handler)

    def set_proxy(self, sock_http):
        """Set sock proxy."""
        onap_proxy = {}
        onap_proxy['http'] = sock_http
        onap_proxy['https'] = sock_http
        self.logger.debug("Scenario - Set proxy %s ", onap_proxy)
        Customer.set_proxy(onap_proxy)

# ----------------------------------------------------------
#
#               YAML UTILS
#
# -----------------------------------------------------------
    @staticmethod
    def get_parameter_from_yaml(parameter, config_file):
        """
        Get the value of a given parameter in file.yaml.

        Parameter must be given in string format with dots
        Example: general.openstack.image_name
        :param config_file: yaml file of configuration
        :return: the value of the parameter
        """
        with open(config_file) as my_file:
            file_yaml = yaml.safe_load(my_file)
        my_file.close()
        value = file_yaml

        # Ugly fix as workaround for the .. within the params in the yaml file
        ugly_param = parameter.replace("..", "##")
        for element in ugly_param.split("."):
            value = value.get(element.replace("##", ".."))
            if value is None:
                raise ValueError("Parameter %s not defined" % parameter)

        return value

    @classmethod
    def get_service_custom_config(cls, *args):
        """
        Get Service related configuration parameters from yaml configuration file.

          * args[0]: service_type (ims, vfw, ansible, mrf, freeradius)
          * args[1]: a parameter, if not specified consider the whole file
        :return: the service custom config
        """
        service_type = args[0]
        try:
            parameter = service_type + "." + args[1]
        except IndexError:
            parameter = service_type
        try:
            local_path = os.path.dirname(os.path.abspath(__file__))
            yaml_ = local_path.replace("src/onaptests/actions",
                                       "templates/vnf-services/" +
                                       service_type + "-service.yaml")
            return cls.get_parameter_from_yaml(parameter, yaml_)
        except FileNotFoundError:
            raise ValueError("Vnf Service file not found")

    @classmethod
    def get_vnf_parameters_from_sdnc(cls, vnf_type, vnf_name):
        """
        Get the VNF parameters for the SDNC preload.

        :param vnf_type: the type of VNF
        :param vnf_name: the name of the VNF
        :return: the VNF paramters
        """
        # Retrieve the parameters for all the vnf of the vnf_type
        vnf_param = []
        all_params = cls.get_service_custom_config(vnf_type, "vnfs")
        # Retrieve only the param corresponding to the vnf_name
        if all_params:
            for vnf in all_params:
                if vnf['vnf_name'].lower() in vnf_name.lower():
                    vnf_param = vnf['vnf_parameters']
        return vnf_param
