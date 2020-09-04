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
            "filename": "./pythonsdk.debug.log",
            "mode": "w"
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console", "file"]
    }
}

# SOCK_HTTP = "socks5h://127.0.0.1:8080"
