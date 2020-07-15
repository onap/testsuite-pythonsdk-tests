# pythonsdk-tests

This project is a wrapper to use onapsdk toolkit to onboard and instantiate services on ONAP

## Temporary help section

A basic example is implemented and is based on 3 python files

* run_onboard.py
* run_instantiate.py
* run_delete.py

The global datas defined in the file
src/onaptests/configuration/settings.py shall be adapted to
your environment.

In addition you must define your service in directory templates/vnf-services
and create zip file for heat template templates/heat_files.
See ubuntu16test as example

### Prepare your environment and run tests

* Clone the project

```shell
git clone https://git.onap.org/testsuite/pythonsdk-tests
```

* virtualenv onboard
* source onboard/bin/activate
* git clone git@gitlab.com:Orange-OpenSource/lfn/onap/python-onapsdk.git -b develop
* cd python-onapsdk
* To install onapsdk package: pip install -e .
* cd ..
* To install onaptests package: pip install -e .
* Set global settings configuration files with all required input datas
  including the dynamic forwarding port for ssh tunnel in
  src/onaptests/configuration/settings.py

```shell
export ONAP_PYTHON_SDK_SETTINGS="onaptests.configuration.settings"
```

* Open ssh tunnel towards your openlab setting a dynamic port forward (by default 1080)

```shell
ssh user@onap.pod4.opnfv.fr -D 1080
```

* Once the different variable datas like service name and instance are updated
in run_*.py files and that the templates files for your service are defined,
start to run the different steps:

  * python run_onboard.py
  * python run_instantiate.py
  * python run_delete.py

* or run the e2e scenario: python run_e2e.py

* By default, all the logs are stored in the file onap_tests.debug.log