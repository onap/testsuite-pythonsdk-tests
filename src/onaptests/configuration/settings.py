"""Specific settings module."""

######################
#                    #
# ONAP INPUTS DATAS  #
#                    #
######################

import random
import string
from jinja2 import Environment, PackageLoader

# Variables to set logger information
# Possible values for logging levels in onapsdk: INFO, DEBUG , WARNING, ERROR
LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "class": "logging.Formatter",
            "format": "%(asctime)s %(levelname)s %(lineno)d:%(filename)s(%(process)d) - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "default"
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": "/tmp/pythonsdk.debug.log",
            "mode": "w"
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console", "file"]
    }
}
CLEANUP_FLAG = False
CLEANUP_ACTIVITY_TIMER = 5
SDC_CLEANUP = False

REPORTING_FILE_DIRECTORY = "/tmp/"
HTML_REPORTING_FILE_NAME = "reporting.html"
JSON_REPORTING_FILE_NAME = "reporting.json"
K8S_REGION_TYPE = "k8s"
TILLER_HOST = "localhost"
K8S_CONFIG = None  # None means it will use default config (~/.kube/config)
K8S_ONAP_NAMESPACE = "onap"  # ONAP Kubernetes namespace
K8S_ADDITIONAL_RESOURCES_NAMESPACE = K8S_ONAP_NAMESPACE  # Resources created on tests namespace
MSB_K8S_OVERRIDE_VALUES = None
# SOCK_HTTP = "socks5h://127.0.0.1:8091"

ORCHESTRATION_REQUEST_TIMEOUT = 60.0 * 15  # 15 minutes in seconds
SERVICE_DISTRIBUTION_NUMBER_OF_TRIES = 30
SERVICE_DISTRIBUTION_SLEEP_TIME = 60
EXPOSE_SERVICES_NODE_PORTS = True
CDS_NODE_PORT = 30449
IN_CLUSTER = False
VES_BASIC_AUTH = {'username': 'sample1', 'password': 'sample1'}
IF_VALIDATION = False
SDNC_SECRET_NAME = "onap-sdnc-db-secret"
SDNC_DB_PRIMARY_HOST = "mariadb-galera.onap.svc.cluster.local"
SDNC_DB_PORT = 3306


# We need to create a service file with a random service name,
# to be sure that we force onboarding
def generate_service_config_yaml_file(service_name: str,
                                      service_template: str,
                                      service_config: str,
                                      generate_random_names: bool = False):
    """Generate service config YAML file.

    Service configurations (both models and instances) are stored in YAML files
        mostly generated by filling Jinja templates with service names. For most
        cases we are generate the same configuration for all runs
        (so generate_random_names is set to False, as default) but it is possible to
        create all resources on each test execution.

    Args:
        service_name (str): Name of the service
        service_template (str): Template which would be used to generate configuration
        service_config (str): Configuration output file path
        generate_random_names (bool, optional): Flag indicating whether service name
            should have a random suffix or not. Defaults to False.

    """

    env = Environment(
        loader=PackageLoader('onaptests', 'templates/vnf-services'),
    )
    template = env.get_template(service_template)

    if generate_random_names:
        # get a random string to randomize the vnf name
        # Random string with the combination of lower and upper case
        letters = string.ascii_letters
        result_str = ''.join(random.choice(letters) for i in range(6))
        service_name = f"{service_name}_{result_str}"

    rendered_template = template.render(service_name=service_name)

    with open(service_config, 'w+', encoding="utf-8") as file_to_write:
        file_to_write.write(rendered_template)
