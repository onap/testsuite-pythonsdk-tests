import uuid
import os
import sys
from pathlib import Path
import openstack
from jinja2 import Environment, PackageLoader
from .settings import *  # pylint: disable=W0614

VNF_FILENAME_PREFIX = "multi-vnf-ubuntu"
SERVICE_NAME = f"multivnfubuntu{str(uuid.uuid4().hex)[:6]}"

CLEANUP_ACTIVITY_TIMER = 15

# We need to create a service file with a random service name,
# to be sure that we force onboarding
def generate_service_config_yaml_file(filename):
    """ generate the service file with a random service name
     from a jinja template"""

    env = Environment(
        loader=PackageLoader('onaptests', 'templates/vnf-services'),
    )
    template = env.get_template(f"{filename}.yaml.j2")

    rendered_template = template.render(service_name=SERVICE_NAME)

    file_name = (sys.path[-1] + "/onaptests/templates/vnf-services/" +
                 f"{filename}.yaml")

    with open(file_name, 'w+') as file_to_write:
        file_to_write.write(rendered_template)


CLEANUP_FLAG = True

CDS_DD_FILE = Path(Path(__file__).parent.parent, "templates/artifacts/dd.json")
CDS_CBA_UNENRICHED = Path(Path(__file__).parent.parent, "templates/artifacts/ubuntuVNF.zip")
CDS_CBA_ENRICHED = "/tmp/UBUNTUVNF_enriched.zip"

ONLY_INSTANTIATE = False
USE_MULTICLOUD = False

CLOUD_REGION_CLOUD_OWNER = "multivnf-macro-cloud-owner"
CLOUD_REGION_TYPE = "openstack"
CLOUD_REGION_VERSION = "pike"
CLOUD_OWNER_DEFINED_TYPE = "N/A"

AVAILABILITY_ZONE_NAME = "multivnf-macro-availability-zone"
AVAILABILITY_ZONE_TYPE = "nova"
COMPLEX_PHYSICAL_LOCATION_ID = "lannion"
COMPLEX_DATA_CENTER_CODE = "1234-5"

GLOBAL_CUSTOMER_ID = "multivnf-customer"

# The cloud Part
# Assuming a cloud.yaml is available, use the openstack client
# to retrieve cloud info and avoid data duplication
TEST_CLOUD = os.getenv('OS_TEST_CLOUD')  # Get values from clouds.yaml
cloud = openstack.connect(cloud=TEST_CLOUD)
VIM_USERNAME = cloud.config.auth.get('username','Fill me')
VIM_PASSWORD = cloud.config.auth.get('password','Fill me')
VIM_SERVICE_URL = cloud.config.auth.get('auth_url','Fill me')
TENANT_ID = cloud.config.auth.get('project_id','Fill me')
TENANT_NAME = cloud.config.auth.get('project_name','Fill me')
CLOUD_REGION_ID = cloud.config.auth.get('region_name','RegionOne')
CLOUD_DOMAIN = cloud.config.auth.get('project_domain_name','Default')

OWNING_ENTITY = "multivnf-oe"
PROJECT = "multivnf-project"
LINE_OF_BUSINESS = "multivnf-lob"
PLATFORM = "multivnf-platform"

VENDOR_NAME = 'ubuntu_xtesting_vendor'

SERVICE_YAML_TEMPLATE = Path(Path(__file__).parent.parent, "templates/vnf-services/" +
                             f"{VNF_FILENAME_PREFIX}-service.yaml")

MODEL_YAML_TEMPLATE = Path(Path(__file__).parent.parent, "templates/vnf-services/" +
                           f"{VNF_FILENAME_PREFIX}-model.yaml")


generate_service_config_yaml_file(f"{VNF_FILENAME_PREFIX}-service")
generate_service_config_yaml_file(f"{VNF_FILENAME_PREFIX}-model")

SERVICE_INSTANCE_NAME = f"{SERVICE_NAME}_svc"
