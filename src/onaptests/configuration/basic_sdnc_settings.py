from .settings import *

CLEANUP_FLAG = True

SERVICE_NAME = "Basic SDNC test"

SERVICE_COMPONENTS = "SDNC"

SERVICE_ID = "pythonsdk-tests-service-01"

SERVICE_STATUS = {
    "rpc-action": "activate",
    "response-message": "test-message-1",
    "response-timestamp": "2023-05-09T13:14:30.540Z",
    "request-status": "synccomplete",
    "final-indicator": "Y",
    "action": "CreateVnfInstance",
    "rpc-name": "vnf-topology-operation",
    "response-code": "200"
}

SERVICE_CHANGED_STATUS = {
    "rpc-action": "activate",
    "response-message": "changed-test-message-1",
    "response-timestamp": "2023-05-09T13:14:30.540Z",
    "request-status": "synccomplete",
    "final-indicator": "Y",
    "action": "CreateVnfInstance",
    "rpc-name": "vnf-topology-operation",
    "response-code": "200"
}

SERVICE_DATA = {
    "service-level-oper-status": {
        "last-rpc-action": "assign",
        "last-action": "CreateServiceInstance",
        "order-status": "Created"
    },
    "service-request-input": {
        "service-input-parameters": {
            "param": [
                {
                    "name": "orchestrator",
                    "value": "multicloud"
                }
            ]
        },
        "service-instance-name": "gnb-93100001"
    }
}

SERVICE_CHANGED_DATA = {
    "service-level-oper-status": {
        "last-rpc-action": "assign",
        "last-action": "CreateServiceInstance",
        "order-status": "Created"
    },
    "service-request-input": {
        "service-input-parameters": {
            "param": [
                {
                    "name": "orchestrator",
                    "value": "multicloud"
                }
            ]
        },
        "service-instance-name": "gnb-93100002"
    }
}
