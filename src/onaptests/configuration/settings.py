"""Specific settings module."""  # pylint: disable=bad-whitespace

######################
#                    #
# ONAP INPUTS DATAS  #
#                    #
######################


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
# Additional flag to enable SDC resources cleanup
# Added as SDC's VSP deletion is broken and most tests fail due to that
# Should be removed as soon as SDC resource deletion is fixed
SDC_CLEANUP = True

REPORTING_FILE_PATH = "/tmp/reporting.html"
K8S_REGION_TYPE = "k8s"
TILLER_HOST = "localhost"
K8S_CONFIG = None  # None means it will use default config (~/.kube/config)
K8S_ONAP_NAMESPACE = "onap"  # ONAP Kubernetes namespace
K8S_ADDITIONAL_RESOURCES_NAMESPACE = K8S_ONAP_NAMESPACE  # Resources created on tests namespace
#SOCK_HTTP = "socks5h://127.0.0.1:8091"

ORCHESTRATION_REQUEST_TIMEOUT = 60.0 * 15  # 15 minutes in seconds
