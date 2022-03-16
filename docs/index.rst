.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. Copyright 2022 Orange Co., Ltd.
.. _master_index:

PYTHONSDK-TESTS Documentation
#############################

Introduction
============

.. important::
    This python module defines Integration automated tests based on the python onapsdk.

ONAP SDK
========

A python ONAP sdk has been developed since the ONAP El Alto version.
Openstack and Kubernetes python SDKs are very popular.
The ambition of the onapsdk was to create a python SDK to interact programmatically
with ONAP APIs.

The onapsdk repository can be found in <https://gitlab.com/Orange-OpenSource/lfn/onap/python-onapsdk>.

The documentation of the onapsdk can be found in <https://python-onapsdk.readthedocs.io/en/latest/?badge=develop>.

This SDK has been developed in gitlab.com to benefit from the numerous built-in
options offered by gitlab and ensure the best possible code quality.

The project is fully Open Source, released under the Apache v2 license.
Integration committers are invited to join the project.
The main maintainers are ONAP integration and OOM committers.

Any new feature shall respect the code quality criteria:

* unit test coverage > 98%
* functional tests (several components mock objects have been developed)

PYTHONSDK-TESTS
===============

Why a pythonsdk-tests project ?
-------------------------------

The SDK is a pure SDK. It offers a way to interact with ONAP through its API.
However it does not provide use cases.
A use case is usually the aggregation of several ONAP API calls.
Pythonsdk-tests was created to define use cases that consume the onap SDK.

It is similar to [Data Provider](https://git.onap.org/integration/data-provider/).

The use cases defined in pythonsdk-tests include an entry point for
[xtesting](https://xtesting.readthedocs.io/en/latest/)
in order to ease the integration in CI chains.

The list and the description of the use cases are defined in <https://docs.onap.org/projects/onap-integration/en/latest/integration-tests.html>.
The pythonsdk-tests can be retrieved as pythonsdk-tests is indicated in the column
Comments.

Project structure
-----------------

The project is a standard python project.

The pythonsdk-tests repository structure can be defined as follows:

  .. code-block:: bash

     .
     ├── AUTHORS
     ├── docs
     │    ├── conf.py
     │    ├── index.rst
     │    └── requirements-docs.txt
     ├── INFO.yaml
     ├── MANIFEST.in
     ├── README.md
     ├── requirements.txt
     ├── run_basic_clamp.py
     ├── run_basic_cnf_macro.py
     ├── run_basic_network_nomulticloud.py
     ├── run_basic_onboard.py
     ├── run_basicvm_multicloud_yaml.py
     ├── run_basicvm_nomulticloud.py
     ├── run_multi_vnf_ubuntu.py
     ├── setup.cfg
     ├── setup.py
     ├── src
     │    └── onaptests
     │        ├── configuration
     │        │    ├── basic_clamp_settings.py
     │        │    ├── basic_cnf_macro_settings.py
     │        │    ├── basic_cnf_macro_yaml_settings.py
     │        │    ├── basic_cnf_yaml_settings.py
     │        │    ├── basic_network_nomulticloud_settings.py
     │        │    ├── basic_onboard_settings.py
     │        │    ├── basic_vm_macro_settings.py
     │        │    ├── basic_vm_macro_stability_settings.py
     │        │    ├── basic_vm_multicloud_yaml_settings.py
     │        │    ├── basic_vm_settings.py
     │        │    ├── cba_enrichment_settings.py
     │        │    ├── cds_resource_resolution_settings.py
     │        │    ├── clearwater_ims_nomulticloud_settings.py
     │        │    ├── multi_vnf_ubuntu_settings.py
     │        │    ├── pnf_macro_settings.py
     │        │    ├── settings.py
     │        │    └── tca-microservice.yaml
     │        ├── masspnfsimulator
     │        ├── scenario
     │        │    ├── basic_clamp.py
     │        │    ├── basic_cnf_macro.py
     │        │    ├── basic_cnf.py
     │        │    ├── basic_network.py
     │        │    ├── basic_onboard.py
     │        │    ├── basic_vm_macro.py
     │        │    ├── basic_vm_macro_stability.py
     │        │    ├── basic_vm.py
     │        │    ├── cds_blueprint_enrichment.py
     │        │    ├── cds_resource_resolution.py
     │        │    ├── clearwater_ims.py
     │        │    ├── multi_vnf_macro.py
     │        │    ├── pnf_macro.py
     │        │    └── usecases
     │        ├── steps
     │        │    ├── base.py
     │        │    ├── cloud
     │        │    ├── instantiate
     │        │    ├── loop
     │        │    ├── onboard
     │        │    ├── reports_collection.py
     │        │    ├── simulator
     │        │    └── wrapper
     │        ├── templates
     │        │    ├── artifacts
     │        │    ├── heat-files
     │        │    ├── helm_charts
     │        │    ├── reporting
     │        │    └── vnf-services
     │        └── utils
     │            ├── exceptions.py
     │            └── resources.py
     ├── tests
     │    ├── data
     │    ├── test_reports_collection.py
     │    ├── test_service_macro_instantiation.py
     │    └── test_store_state.py

The README.md indicates how to execute the tests and more specifically
how to set the required environment variables.

The configuration directory contains all the required parameters per test.

Some use case can be run directly.

  .. code-block:: python

    python run_basic_cnf_macro.py

All the use cases can be run through xtesting framework. . Usually The xtesting
entry points are defined as python module entrypoint in the setup.cfg

  .. code-block:: bash
    [entry_points]
    xtesting.testcase =
      basic_vm = onaptests.scenario.basic_vm:BasicVm
      basic_vm_macro = onaptests.scenario.basic_vm_macro:BasicVmMacro
      basic_vm_macro_stability = onaptests.scenario.basic_vm_macro_stability:BasicVmMacroStability
      basic_network = onaptests.scenario.basic_network:BasicNetwork
      basic_cnf = onaptests.scenario.basic_cnf:BasicCnf
      basic_cds =  onaptests.scenario.cds_blueprint_enrichment:CDSBlueprintEnrichment
      clearwater_ims = onaptests.scenario.clearwater_ims:ClearwaterIms
      basic_onboard = onaptests.scenario.basic_onboard:BasicOnboard
      pnf_macro = onaptests.scenario.pnf_macro:PnfMacro
      basic_clamp = onaptests.scenario.basic_clamp:BasicClamp
      cds_resource_resolution = onaptests.scenario.cds_resource_resolution:CDSResourceResolution
      multi_vnf_ubuntu_macro = onaptests.scenario.multi_vnf_macro:MultiVnfUbuntuMacro
      basic_cnf_macro = onaptests.scenario.basic_cnf_macro:BasicCnfMacro

The classes corresponding to these entry points can be found in the src/onaptests/scenario directory.

The use case can be executed as follows:

  .. code-block:: bash

    run_tests -t run_basic_cnf_macro.py

Modular architecture
--------------------

Moreover, as ONAP tests usually are base on similar sequences, it was decided
to adopt a modular architecture and define "steps" that could be reused from
one test to another.

When basic_onboard is composed of the following steps:

* [SDC] YamlTemplateServiceOnboardStep: Onboard service described in YAML file in SDC
* [SDC] YamlTemplateVfOnboardStep: Onboard vf described in YAML file in SDC
* [SDC] YamlTemplateVspOnboardStep: Onboard vsp described in YAML file in SDC
* [SDC] VendorOnboardStep: Onboard vendor in SDC

These 4 steps are also reused in basic_vm_macro:

* [SO] YamlTemplateServiceMacroInstantiateStep cleanup: Instantiate service described in YAML using SO macro method
* [CDS] CbaEnrichStep cleanup: Enrich CBA file
* [SO] YamlTemplateServiceMacroInstantiateStep: Instantiate service described in YAML using SO macro method
* [AAI] ConnectServiceSubToCloudRegionStep: Connect service subscription with cloud region
* [AAI] CustomerServiceSubscriptionCreateStep: Create customer's service subscription
* [AAI] CustomerCreateStep: Create customer
* [AAI] LinkCloudRegionToComplexStep: Connect cloud region with complex
* [AAI] ComplexCreateStep: Create complex
* [AAI] RegisterCloudRegionStep: Register cloud region
* [AAI] CloudRegionCreateStep: Create cloud region
* [SDC] YamlTemplateServiceOnboardStep: Onboard service described in YAML file in SDC
* [SDC] YamlTemplateVfOnboardStep: Onboard vf described in YAML file in SDC
* [SDC] YamlTemplateVspOnboardStep: Onboard vsp described in YAML file in SDC
* [SDC] VendorOnboardStep: Onboard vendor in SDC
* [CDS] CbaPublishStep: Publish CBA file
* [CDS] CbaEnrichStep: Enrich CBA file
* [CDS] DataDictionaryUploadStep: Upload data dictionaries to CloudRegionCreateStep
* [CDS] BootstrapBlueprintprocessor: Bootstrap CDS blueprintprocessor
* [CDS] ExposeCDSBlueprintprocessorNodePortStep: Expose CDS blueprintsprocessor NodePort

All the steps are defined in the src/onaptests/steps directory.
For example, the step [SDC] VendorOnboardStep: Onboard vendor in SDC is defined in
src/onaptests/steps/onboard/vendor.py

  .. code-block:: python

    from onapsdk.configuration import settings
    from onapsdk.sdc.vendor import Vendor

    from ..base import BaseStep


    class VendorOnboardStep(BaseStep):
        """Vendor onboard step."""

        @property
        def description(self) -> str:
            """Step description."""
            return "Onboard vendor in SDC."

        @property
        def component(self) -> str:
            """Component name."""
            return "SDC"

        @BaseStep.store_state
        def execute(self):
            """Onboard vendor."""
            super().execute()
            vendor: Vendor = Vendor(name=settings.VENDOR_NAME)
            vendor.onboard()

We can see here the call to the onapsdk through the definition of the Vendor
object and the call to the onboard() function associated with this object.

Steps may trigger sub steps, as an example you can create a VNF
(YamlTemplateVnfAlaCarteInstantiateStep) only if a service
(YamlTemplateServiceAlaCarteInstantiateStep) has been defined.

  .. code-block:: python

     class YamlTemplateVnfAlaCarteInstantiateStep(YamlTemplateBaseStep):
         """Instantiate vnf a'la carte using YAML template."""

         def __init__(self, cleanup=False):
             """Initialize step.

             Substeps:
                 - YamlTemplateServiceAlaCarteInstantiateStep.
             """
             super().__init__(cleanup=cleanup)
             self._yaml_template: dict = None
             self._service_instance_name: str = None
             self._service_instance: ServiceInstance = None
             self.add_step(YamlTemplateServiceAlaCarteInstantiateStep(cleanup))



How to create a test ?
----------------------

You can compose your test by using existing steps and/or create your own steps.
In the example hereafter, the test could be defined as indicated, a new class
implementing mySuperTestStep shall be defined. Just check that the step you have
in mind does not already exist.

  .. code-block:: python

     import logging.config
     import onaptests.utils.exceptions as onap_test_exceptions
     from onapsdk.configuration import settings
     from onaptests.steps.onboard.service import YamlTemplateServiceOnboardStep

     if __name__ == "__main__":
         logging.config.dictConfig(settings.LOG_CONFIG)
         logger = logging.getLogger("My super test")
         my_super_test = mySuperTestStep(
             cleanup=settings.CLEANUP_FLAG)
         try:
             my_super_test.execute()
         except onap_test_exceptions.TestConfigurationException:
             logger.error("My super test configuration error")
         my_super_test.reports_collection.generate_report()
