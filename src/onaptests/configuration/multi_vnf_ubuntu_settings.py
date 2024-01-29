import uuid
import os
from pathlib import Path
import openstack
from jinja2 import Environment, PackageLoader
from onaptests.utils.resources import get_resource_location
from .settings import IF_VALIDATION
from .settings import *  # noqa


VNF_FILENAME_PREFIX = "multi-vnf-ubuntu"
SERVICE_NAME = f"multivnfubuntu{str(uuid.uuid4().hex)[:6]}"
SERVICE_DETAILS = "Onboarding, distribution and instanitation of an Mutli VM service using macro"


# We need to create a service file with a random service name,
# to be sure that we force onboarding
def generate_service_config_yaml_file(filename):
    """generate the service file with a random service name
     from a jinja template"""

    env = Environment(
        loader=PackageLoader('onaptests', 'templates/vnf-services'),
    )
    template = env.get_template(f"{filename}.yaml.j2")

    rendered_template = template.render(service_name=SERVICE_NAME)

    file_name = get_resource_location(f"templates/vnf-services/{filename}.yaml")

    with open(file_name, 'w+', encoding="utf-8") as file_to_write:
        file_to_write.write(rendered_template)


CLEANUP_FLAG = True

CDS_DD_FILE = Path(get_resource_location("templates/artifacts/dd_nso_ubuntu.json"))
CDS_CBA_UNENRICHED = Path(get_resource_location("templates/artifacts/nso_ubuntuvnf.zip"))
CDS_CBA_ENRICHED = "/tmp/UBUNTUVNF_enriched.zip"

ONLY_INSTANTIATE = False
USE_MULTICLOUD = False

CLOUD_REGION_CLOUD_OWNER = "Bell-IaaS"
CLOUD_REGION_TYPE = "openstack"
CLOUD_REGION_VERSION = "v1"
CLOUD_OWNER_DEFINED_TYPE = "VNF"

AVAILABILITY_ZONE_NAME = "z1"
AVAILABILITY_ZONE_TYPE = "nova"
COMPLEX_PHYSICAL_LOCATION_ID = "nso-lab-ltec"
COMPLEX_DATA_CENTER_CODE = "nlt"

GLOBAL_CUSTOMER_ID = "ubuntu-customer"

if not IF_VALIDATION:
    TEST_CLOUD = os.getenv('OS_TEST_CLOUD')  # Get values from clouds.yaml
    cloud = openstack.connect(cloud=TEST_CLOUD)
    VIM_USERNAME = cloud.config.auth.get('username', 'nso')
    VIM_PASSWORD = cloud.config.auth.get('password', 'Password123')
    VIM_SERVICE_URL = cloud.config.auth.get('auth_url', 'https://10.195.194.215:5000')
    TENANT_ID = cloud.config.auth.get('project_id', 'e2710e84063b421fab08189818761d55')
    TENANT_NAME = cloud.config.auth.get('project_name', 'nso')
    CLOUD_REGION_ID = cloud.config.auth.get('region_name', 'nso215')
    CLOUD_DOMAIN = cloud.config.auth.get('project_domain_name', 'Default')

OWNING_ENTITY = "seb"
PROJECT = "Project-UbuntuDemo"
LINE_OF_BUSINESS = "wireless"
PLATFORM = "iaas-openstack"
CLOUD_DOMAIN = "Default"

VENDOR_NAME = 'ubuntu_xtesting_vendor'

SERVICE_YAML_TEMPLATE = Path(get_resource_location("templates/vnf-services/" +
                             f"{VNF_FILENAME_PREFIX}-service.yaml"))

MODEL_YAML_TEMPLATE = Path(get_resource_location("templates/vnf-services/" +
                           f"{VNF_FILENAME_PREFIX}-model.yaml"))


generate_service_config_yaml_file(f"{VNF_FILENAME_PREFIX}-service")
generate_service_config_yaml_file(f"{VNF_FILENAME_PREFIX}-model")

SERVICE_INSTANCE_NAME = f"{SERVICE_NAME}_svc"
