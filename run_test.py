import configparser
import importlib
import logging.config
import os
import sys

from onapsdk.exceptions import ModuleError
import onaptests.utils.exceptions as onap_test_exceptions

SETTING_FILE_EXCEPTIONS = {
    "clearwater_ims": "clearwater_ims_nomulticloud_settings",
    "basic_cnf": "basic_cnf_yaml_settings",
    "basic_cds": "cba_enrichment_settings",
    "basic_network": "basic_network_nomulticloud_settings",
    "multi_vnf_macro": "multi_vnf_ubuntu_settings"
}

MODULES_TO_RELOAD = [
    "onapsdk",
    "onaptests"
]

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

def run_test(test_name, validation, force_cleanup, entry_point):
    settings_env = "ONAP_PYTHON_SDK_SETTINGS"
    if force_cleanup:
        validation_env = "PYTHON_SDK_TESTS_FORCE_CLEANUP"
        os.environ[validation_env] = "True"

    setting_file_name = f"{test_name}_settings"
    if test_name in SETTING_FILE_EXCEPTIONS:
        setting_file_name = SETTING_FILE_EXCEPTIONS[test_name]
    os.environ[settings_env] = f"onaptests.configuration.{setting_file_name}"
    try:
        basic_settings = importlib.import_module("onaptests.configuration.settings")
        if validation:
            basic_settings.IF_VALIDATION = True
        settings_module = importlib.import_module("onapsdk.configuration")
    except ModuleError:
        raise onap_test_exceptions.TestConfigurationException(
            f"Expected setting file {os.environ[settings_env]} not found")

    if validation:
        settings_module.settings.CLEANUP_FLAG = True
        settings_module.settings.CLEANUP_ACTIVITY_TIMER = 1
        settings_module.settings.SDC_CLEANUP = True
        settings_module.settings.SERVICE_DISTRIBUTION_SLEEP_TIME = 1

    # logging configuration for onapsdk, it is not requested for onaptests
    # Correction requested in onapsdk to avoid having this duplicate code
    logging.config.dictConfig(settings_module.settings.LOG_CONFIG)
    logger = logging.getLogger(test_name)
    logger.info(f"Running {test_name} test")

    test_module = importlib.import_module(entry_point["module"])

    test_instance = getattr(test_module, entry_point["class"])()
    if validation:
        validate_scenario_base_class(test_name, test_instance)
    test_instance.run()
    test_instance.clean()
    if validation:
        logger.info(f"Validating {test_name} test")
        test_instance.validate()

def validate_scenario_base_class(test_name, scenario):
    has_scenario_base = False
    for base in scenario.__class__.__bases__:
        if base.__name__ in "ScenarioBase":
            has_scenario_base = True
            break
    if not has_scenario_base:
        raise TestConfigurationException(
            f"[{test_name}] {scenario.__class__.__name__} class does not inherit from ScenarioBase")

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
        modules_reload = False
        for test_name, entry_point in entry_points.items():
            if modules_reload:
                modules_to_keep = dict()
                for module in sys.modules:
                    reload_module = False
                    for module_to_reload in MODULES_TO_RELOAD:
                        if module_to_reload in module:
                            reload_module = True
                            break
                    if not reload_module:
                        modules_to_keep[module] = sys.modules[module]
                sys.modules.clear()
                sys.modules.update(modules_to_keep)
            run_test(
                test_name, validation, force_cleanup, entry_point)
            modules_reload = True
    else:
        entry_point = entry_points[test_name]
        run_test(test_name, validation, force_cleanup, entry_point)

if __name__ == "__main__":
    main(sys.argv[1:])
