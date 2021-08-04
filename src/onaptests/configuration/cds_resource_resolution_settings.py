from pathlib import Path
from uuid import uuid4

from .settings import *  # pylint: disable=W0614

CLEANUP_FLAG = True
SERVICE_NAME = "CDS resource resolution"
CLOUD_REGION_CLOUD_OWNER = "basicnf-owner" # must not contain _
CLOUD_REGION_ID = "k8sregion"
CLOUD_REGION_TYPE = "k8s"
CLOUD_REGION_VERSION = "1.0"
CLOUD_OWNER_DEFINED_TYPE = "N/A"
COMPLEX_PHYSICAL_LOCATION_ID = "sdktests"

MSB_K8S_DEFINITION_ATRIFACT_FILE_PATH = Path(Path(__file__).parent.parent,
                                            "templates/artifacts/cds-resource-resolution/cds-mock-server.tar.gz")
MSB_K8S_RB_NAME = f"cds-ms-rb-{str(uuid4())}"
MSB_K8S_RB_VERSION = "v1"
MSB_K8S_PROFILE_ARTIFACT_FILE_PATH = Path(Path(__file__).parent.parent,
                                        "templates/artifacts/profile.tar.gz")
MSB_K8S_PROFILE_NAME = f"cds-ms-prof-{str(uuid4())}"
K8S_VERSION = "1.0"
K8S_CONFIG = str(Path(Path(__file__).parent.parent, "templates/artifacts/config"))
K8S_ADDITIONAL_RESOURCES_NAMESPACE = "onap-tests"
CDS_MOCKSERVER_EXPECTATIONS = [
    {
        "method": "GET",
        "path": "/resource-resolution/get",
        "response": '{"value": "A046E51D-44DC-43AE-BBA2-86FCA86C5265"}'
    },
    {
        "method": "GET",
        "path": "/resource-resolution/get/A046E51D-44DC-43AE-BBA2-86FCA86C5265/id",
        "response": '{"value": "74FE67C6-50F5-4557-B717-030D79903908"}'
    },
    {
        "method": "POST",
        "path": "/resource-resolution/post",
        "response": '{"value": "post:ok"}'
    },
    {
        "method": "PUT",
        "path": "/resource-resolution/put",
        "response": '{"value": "put:ok"}'
    },
    {
        "method": "PATCH",
        "path": "/resource-resolution/patch",
        "response": '{"value": "patch:ok"}'
    },
    {
        "method": "DELETE",
        "path": "/resource-resolution/delete",
        "response": '{"value": "delete:ok"}'
    }
]

CDS_DD_FILE = Path(Path(__file__).parent.parent, "templates/artifacts/cds-resource-resolution/dd.json")
CDS_CBA_UNENRICHED = Path(Path(__file__).parent.parent, "templates/artifacts/cds-resource-resolution/resource-resolution.zip")
CDS_CBA_ENRICHED = "/tmp/resource-resolution-enriched.zip"
CDS_WORKFLOW_NAME = "resource-resolution"
CDS_WORKFLOW_INPUT = {
    "template-prefix": [
        "helloworld-velocity",
        "helloworld-jinja"
    ],
    "resolution-key": "regression-test",
    "resource-resolution-properties": {
        "v_input": "ok",
        "j_input": "ok"
    }
}
CDS_WORKFLOW_EXPECTED_OUTPUT  = {
    "resource-resolution-response": {
        "meshed-template": {
            "helloworld-velocity": "{\n  \"default\": \"ok\",\n  \"input\": \"ok\",\n  \"script\": {\n    \"python\": \"ok\",\n    \"kotlin\": \"ok\"\n  },\n  \"db\": \"ok\",\n  \"rest\": {\n    \"GET\": \"A046E51D-44DC-43AE-BBA2-86FCA86C5265\",\n    \"POST\": \"post:ok\",\n    \"PUT\": \"put:ok\",\n    \"PATCH\": \"patch:ok\",\n    \"DELETE\": \"delete:ok\"\n  }\n}\n",
            "helloworld-jinja": "{\n  \"default\": \"ok\",\n  \"input\": \"ok\",\n  \"script\": {\n    \"python\": \"ok\",\n    \"kotlin\": {\n      \"base\": \"ok\"\n      \"from suspend function\": \"ok\"\n    }\n  },\n  \"db\": \"ok\",\n  \"rest\": {\n    \"GET\": \"A046E51D-44DC-43AE-BBA2-86FCA86C5265\",\n    \"GET_ID\": \"74FE67C6-50F5-4557-B717-030D79903908\",\n    \"POST\": \"post:ok\",\n    \"PUT\": \"put:ok\",\n    \"PATCH\": \"patch:ok\",\n    \"DELETE\": \"delete:ok\"\n  }\n}\n"
        }
    }
}
