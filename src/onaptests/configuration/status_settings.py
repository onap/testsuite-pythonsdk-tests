from .settings import * # pylint: disable=W0614

""" Specific Status Check settings."""
SERVICE_NAME = "Status Check"
SERVICE_DETAILS = "Checks status of all k8s resources in the selected namespace"
SERVICE_COMPONENTS = "ALL"
STATUS_RESULTS_DIRECTORY = "src/"