import logging
import time
import json

from onapsdk.configuration import settings
from onapsdk.exceptions import SDKException
from onaptests.scenario.scenario_base import ScenarioBase
from onapsdk.onap_service import OnapService
from onaptests.steps.base import BaseStep
from onaptests.utils.exceptions import OnapTestException
from onapsdk.exceptions import RelationshipNotFound, ResourceNotFound




class TestAnalyseStep(BaseStep, OnapService):
    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        """Init ResultsAnalyserStep."""
        super().__init__(cleanup=False)

    @property
    def component(self) -> str:
        """Component name."""
        return "ALL"

    @property
    def description(self) -> str:
        """Step description."""
        return "Analys results of all the tests executed in the testsuite"

    def execute(self):
        super().execute()

        failed_components = []

        response_id = self.send_message_json(
            "GET",
            "GET execution id",
            f"{settings.EXECUTION_ID_URL}"
        )
     
        execution = response_id['results'][0]['execution']
        failed_test_ids = [test['id'] for test in execution if test['status'] == 'failed' and test['name'] != 'run:/basic-status' ]
        failed_status_id = [test['id'] for test in execution if test['name'] == 'run:/basic-status' and test['status'] == 'failed']

        for test_id in failed_test_ids:
            response_test = self.send_message_json(
                "GET",
                "failed components in reporting.json",
                f"{settings.TESTKUBE_URL}/{test_id}/{settings.TEST_RESULTS_URL}"
            )
            if 'steps' in response_test:
                failed_components += [step['component'] for step in response_test['steps'] if step['status'] == 'FAIL']

        response_status = self.send_message_json(
                "GET",
                "failed components in status-details.json",
                f"{settings.TESTKUBE_URL}/{failed_status_id[0]}/{settings.STATUS_RESULTS_URL}"
            )

        if failed_components:
            self._logger.warning("Components failed:")
            for component in failed_components:
                self._logger.warning(component)

        component_mapping = {
            "job": "Job",
            "pod": "Pod",
            "service": "Service",
            "deployment": "Deployment",
            "replicaset": "ReplicaSet",
            "statefulset": "StatefulSet",
            "daemonset": "DaemonSet",
            "configmap": "ConfigMap",
            "secret": "Secret",
            "ingress": "Ingress",
            "pvc": "PVC"
        }
        for component, component_name in component_mapping.items():
            if response_status[component]["number_failing"] > 0:
                self._logger.warning(f"Failed {component_name}s:")
                for item in response_status[component]["failing"]:
                    self._logger.warning(f"{component_name} failed: {item}")


class ResultsAnalyser(ScenarioBase):
    """Run analysis of tests run in the testsuite"""

    __logger = logging.getLogger()

    def __init__(self, **kwargs):
        """Init Results' Analysis use case."""
        super().__init__('result_analysis', **kwargs)
        self.test = TestAnalyseStep(cleanup=settings.CLEANUP_FLAG)

    def run(self):
        """Run results' analysis test."""
        self.start_time = time.time()
        try:
            self.test.execute()
            self.test.cleanup()
            self.result = 100
        except OnapTestException as exc:
            self.result = 0
            self.__logger.exception(exc.error_message)
        except SDKException:
            self.result = 0
            self.__logger.exception("SDK Exception")
        finally:
            self.stop_time = time.time()

    def clean(self):
        """Generate report."""
        self.test.reports_collection.generate_report()