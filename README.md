# pythonsdk-tests

This project is a wrapper to use onapsdk toolkit to onboard and
instantiate services on ONAP

## Temporary help section

A basic example is implemented in the python file

- run_basicvm_multicloud_yaml.py

The global datas defined in these files (see input_datas) shall be
adapted to your environment.

In addition you must define your service in directory templates/vnf-services
and create zip file for heat template templates/heat_files.
See ubuntu16test as example

### Prepare your environment and run tests

- Clone the project (using instantiation branch)
  ```shell
  git clone https://gerrit.onap.org/r/testsuite/pythonsdk-tests.git
  ```

- Create a virtual environment and clone the python-onapsdk
  ```shell
  virtualenv my_test
  source my_test/bin/activate
  git clone git@gitlab.com:Orange-OpenSource/lfn/onap/python-onapsdk.
  git -b develop
  cd python-onapsdk
  pip install -e .
  cd ..
  pip install -e .
  ```

- Set global settings configuration files with all required input datas
  including the dynamic forwarding port for ssh tunnel in
  src/onaptests/configuration/settings.py

- Export the setting file in a environment variable
  ```shell
  export ONAP_PYTHON_SDK_SETTINGS="onaptests.configuration.ubuntu16_multicloud_yaml_settings"
  ```

Note each "use case" may have its own settings corresponding to the test
environment and configuration.

- (optional) Open ssh tunnel towards your openlab setting a dynamic
  port forward (by default 1080):
  ```shell
  ssh user@onap.pod4.opnfv.fr -D 1080
  ```

- Once the different input datas are updated in run\_\*.py files and
  that the templates files for your service are defined, start to run
  the different steps:
  ```shell
  python run.py
  ```

- By default, all the logs are stored in the file pythonsdk.debug.log.
  The file name and location can be set in the settings.py
