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

REPORTING_FILE_PATH = "/tmp/reporting.html"
K8S_REGION_TYPE = "k8s"
K8S_CONFIG = None  # None means it will use default config (~/.kube/config)
K8S_NAMESPACE = "onap"  # Kubernetes namespace
<<<<<<< HEAD   (fcb7ff Merge "Nodeport cleanup in basic_cds test" into guilin)
# SOCK_HTTP = "socks5h://127.0.0.1:8080"
=======
#SOCK_HTTP = "socks5h://127.0.0.1:8091"
>>>>>>> CHANGE (ff24de [PythonSDK-tests] Add basic_onboard testcase)
