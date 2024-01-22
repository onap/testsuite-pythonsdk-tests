import configparser
import importlib
import logging.config
import os
import sys

import onaptests.utils.exceptions as onap_test_exceptions


def get_entrypoints():
    config = configparser.ConfigParser()
    config.read('setup.cfg')
    entry_points = config['entry_points']['xtesting.testcase']
    config = configparser.ConfigParser()
    config.read_string(f"[entry_points]\n{entry_points}")
    entry_points = config['entry_points']
    entry_points_result = {}
    for test_name, entrypoint in entry_points.items():
        test_scenario_module, test_class = entrypoint.split(":")
        entry_points_result[test_name] = {
            "module": test_scenario_module,
            "class": test_class
        }
    return entry_points_result

def run_test(test_name, validation, force_cleanup, entry_point, settings_module):
    settings_env = "ONAP_PYTHON_SDK_SETTINGS"
    if validation:
        validation_env = "PYTHON_SDK_TESTS_VALIDATION"
        os.environ[validation_env] = "True"
    if force_cleanup:
        validation_env = "PYTHON_SDK_TESTS_FORCE_CLEANUP"
        os.environ[validation_env] = "True"
    os.environ[settings_env] = f"onaptests.configuration.{test_name}_settings"
    if not settings_module:
        settings_module = importlib.import_module("onapsdk.configuration")
    else:
        settings_module = importlib.reload(settings_module)
    settings = settings_module.settings
    # logging configuration for onapsdk, it is not requested for onaptests
    # Correction requested in onapsdk to avoid having this duplicate code
    logging.config.dictConfig(settings.LOG_CONFIG)
    logger = logging.getLogger(test_name)
    logger.info(f"Running {test_name} test")

    test_module = importlib.import_module(entry_point["module"])

    test_instance = getattr(test_module, entry_point["class"])()
    try:
        test_instance.run()
        test_instance.clean()
        if validation:
            test_instance.validate_execution()
    except onap_test_exceptions.TestConfigurationException:
        logger.error("Status Check configuration error")
    return settings_module

def main(argv):
    """Script is used to run one or all the tests.
    
    You need to specify a name of the test like 'basic_cps' or
    keyword 'all' that tells to run all the tests. You can also
    pass a second argument of any value that tells the script to run
    test(s) in the validation mode that checks only a basic setup of
    steps (like cleanup) and their execution in a certain order.

    Examplary use:
    - python run_test.py basic_vm_macro
    - python run_test.py basic_cps validation
    - python run_test.py all true
    """
    if len(argv) == 0:
        print("Required test name argument missing", file=sys.stderr)
        print("\nExample: python run_test.py basic_cps\n")
        exit(1)
    validation = len(argv) > 1
    force_cleanup = len(argv) > 2
    test_name = argv[0]
    entry_points = get_entrypoints()
    if test_name == "all":
        settings_module = None
        for test_name, entry_point in entry_points.items():
            settings_module = run_test(test_name, validation, force_cleanup, entry_point, settings_module)
    else:
        entry_point = entry_points[test_name]
        run_test(test_name, validation, force_cleanup, entry_point, None)

if __name__ == "__main__":
    main(sys.argv[1:])
