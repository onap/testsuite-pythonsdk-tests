from .settings import * # pylint: disable=W0614

""" Specific results' analysis settings """
SERVICE_NAME = "Results Analysis"
SERVICE_DETAILS = "Check results of other tests run in the testsuite"
SERVICE_COMPONENTS = "ALL"

IN_CLUSTER = True

EXECUTION_ID_URL = "https://testkube-tnap-dev-02.tnaplab.telekom.de/v1/test-suites/tnap-testsuite/executions"
TESTKUBE_URL = "https://testkube-tnap-dev-02.tnaplab.telekom.de/v1/executions"
STATUS_RESULTS_URL = "artifacts/status-details.json"
TEST_RESULTS_URL = "artifacts/reporting.json"
