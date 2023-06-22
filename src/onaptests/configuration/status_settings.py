from .settings import * # pylint: disable=W0614

""" Specific Status Check """
SERVICE_NAME = "Status Check"
SERVICE_DETAILS = "Checks status of all k8s resources in the selected namespace"
SERVICE_COMPONENTS = "ALL"
STATUS_RESULTS_DIRECTORY = "/tmp"
STORE_ARTIFACTS = True
CHECK_POD_VERSIONS = True
IGNORE_EMPTY_REPLICAS = False
STATUS_DETAILS_JSON = "status-details.json"

FULL_LOGS_CONTAINERS = [
    'dcae-bootstrap', 'dcae-cloudify-manager', 'aai-resources',
    'aai-traversal', 'aai-modelloader', 'sdnc', 'so', 'so-bpmn-infra',
    'so-openstack-adapter', 'so-sdc-controller', 'mariadb-galera', 'sdc-be',
    'sdc-fe'
]

# patterns to be excluded from the check
WAIVER_LIST = ['integration']

SPECIFIC_LOGS_CONTAINERS = {
    'sdc-be': ['/var/log/onap/sdc/sdc-be/error.log'],
    'sdc-onboarding-be': ['/var/log/onap/sdc/sdc-onboarding-be/error.log'],
    'aaf-cm': [
        '/opt/app/osaaf/logs/cm/cm-service.log',
        '/opt/app/osaaf/logs/cm/cm-init.log'
    ],
    'aaf-fs': [
        '/opt/app/osaaf/logs/fs/fs-service.log',
        '/opt/app/osaaf/logs/fs/fs-init.log'
    ],
    'aaf-locate': [
        '/opt/app/osaaf/logs/locate/locate-service.log',
        '/opt/app/osaaf/logs/locate/locate-init.log'
    ],
    'aaf-service': [
        '/opt/app/osaaf/logs/service/authz-service.log',
        '/opt/app/osaaf/logs/service/authz-init.log'
    ],
    'sdc-be': [
        '/var/log/onap/sdc/sdc-be/debug.log',
        '/var/log/onap/sdc/sdc-be/error.log'
    ],
    'sdc-fe': [
        '/var/log/onap/sdc/sdc-fe/debug.log',
        '/var/log/onap/sdc/sdc-fe/error.log'
    ],
    'vid': [
        '/var/log/onap/vid/audit.log',
        '/var/log/onap/vid/application.log',
        '/var/log/onap/vid/debug.log',
        '/var/log/onap/vid/error.log'
    ],
}

DOCKER_REPOSITORIES = [
    'nexus3.onap.org:10001', 'docker.elastic.co', 'docker.io', 'library',
    'registry.gitlab.com', 'registry.hub.docker.com', 'k8s.gcr.io', 'gcr.io'
]
DOCKER_REPOSITORIES_NICKNAMES = {
    'nexus3.onap.org:10001': 'onap',
    'docker.elastic.co': 'elastic',
    'docker.io': 'dockerHub (docker.io)',
    'registry.hub.docker.com': 'dockerHub (registry)',
    'registry.gitlab.com': 'gitlab',
    'library': 'dockerHub (library)',
    'default': 'dockerHub',
    'k8s.gcr.io': 'google (k8s.gcr)',
    'gcr.io': 'google (gcr)'
}

GENERIC_NAMES = {
    'postgreSQL': ['crunchydata/crunchy-postgres', 'postgres'],
    'mariadb': ['adfinissygroup/k8s-mariadb-galera-centos', 'mariadb'],
    'elasticsearch': [
        'bitnami/elasticsearch', 'elasticsearch/elasticsearch',
        'onap/clamp-dashboard-elasticsearch'
    ],
    'nginx': ['bitnami/nginx', 'nginx'],
    'cassandra': [
        'cassandra', 'onap/music/cassandra_3_11', 'onap/music/cassandra_music',
        'onap/aaf/aaf_cass'
    ],
    'zookeeper': ['google_samples/k8szk', 'onap/dmaap/zookeeper', 'zookeeper'],
    'redis': [
        'onap/vfc/db',
        'onap/org.onap.dcaegen2.deployments.redis-cluster-container'
    ],
    'consul': ['consul', 'oomk8s/consul'],
    'rabbitmq': ['ansible/awx_rabbitmq', 'rabbitmq']
}

MAX_LOG_BYTES = 512000

UNLIMITED_LOG_BYTES = 10**10 # 10 GB
