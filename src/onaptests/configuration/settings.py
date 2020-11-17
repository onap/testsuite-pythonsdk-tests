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

REPORTING_FILE_PATH = "/tmp/reporting.html"
K8S_REGION_TYPE = "k8s"
# SOCK_HTTP = "socks5h://127.0.0.1:8080"
PNF_VES_CONFIG = dict(
            count=1,
            vesprotocol="https",
            vesip="ves.api.simpledemo.onap.org",
            vesport="30417",
            vesresource="eventListener",
            vesversion="v7",
            ipstart="10.11.0.16",
            user="sample1",
            password="sample1",
            ipfileserver="127.0.0.1",
            typefileserver="sftp"
        )
