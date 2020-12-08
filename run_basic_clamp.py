#!/usr/bin/python
#
import logging.config
from onapsdk.configuration import settings
from onaptests.steps.loop.clamp import ClampStep


if __name__ == "__main__":
    # logging configuration for onapsdk, it is not requested for onaptests
    # Correction requested in onapsdk to avoid having this duplicate code
    logging.config.dictConfig(settings.LOG_CONFIG)
    logger = logging.getLogger("Instantiate Basic Clamp")

    basic_clamp = ClampStep(
        cleanup=settings.CLEANUP_FLAG)
    basic_clamp.execute()
    basic_clamp.reports_collection.generate_report()
