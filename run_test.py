import configparser
import importlib
import logging.config
import os
import sys

import onaptests.utils.exceptions as onap_test_exceptions


def run_test(test_name, validation):
    settings_env = "ONAP_PYTHON_SDK_SETTINGS"
    if validation:
        validation_env = "PYTHON_SDK_TESTS_VALIDATION"
        os.environ[validation_env] = "True"
    os.environ[settings_env] = f"onaptests.configuration.{test_name}_settings"
    settings = importlib.import_module("onapsdk.configuration").settings
    logging.config.dictConfig(settings.LOG_CONFIG)
    logger = logging.getLogger(test_name)
    logger.info(f"Running {test_name} test")

    config = configparser.ConfigParser()
    config.read('setup.cfg')
    entry_points = config['entry_points']['xtesting.testcase']
    config.read_string(f"[entry_points]\n{entry_points}")
    entry_points = config['entry_points']
    test_scenario_module, test_class = entry_points[test_name].split(":")
    test_module = importlib.import_module(test_scenario_module)

    test_instance = getattr(test_module, test_class)()
    try:
        test_instance.run()
        test_instance.clean()
        if validation:
            test_instance.validate_execution()
    except onap_test_exceptions.TestConfigurationException:
        logger.error("Status Check configuration error")

def main(argv):
    # logging configuration for onapsdk, it is not requested for onaptests
    # Correction requested in onapsdk to avoid having this duplicate code
    if len(argv) == 0:
        print("Required test name argument missing", file=sys.stderr)
        print("\nExample: python run_test.py basic_cps\n")
        exit(1)
    validation = len(argv) > 1
    test_name = argv[0]
    run_test(test_name, validation)

if __name__ == "__main__":
    main(sys.argv[1:])
