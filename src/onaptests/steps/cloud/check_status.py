#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
import json
import os
import logging
import re
from onapsdk.configuration import settings
from natural.date import delta
from xtesting.core import testcase
from kubernetes import client, config
from kubernetes.stream import stream
from urllib3.exceptions import MaxRetryError, NewConnectionError
from jinja2 import Environment, PackageLoader, select_autoescape

from ..base import BaseStep
from .resources import Pod, Container, Service, Job
from .resources import Deployment, StatefulSet, DaemonSet, Pvc, ReplicaSet
from .resources import ConfigMap, Secret, Ingress
from onaptests.utils.exceptions import StatusCheckException

NAMESPACE = settings.K8S_ONAP_NAMESPACE

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


class CheckNamespaceStatusStep(BaseStep):
    """Check status of all k8s resources in the selected namespace."""

    __logger = logging.getLogger(__name__)

    def __init__(self, cleanup: bool = False,**kwargs):
        """Init CheckNamespaceStatusStep."""
        super().__init__(cleanup=cleanup)

        if settings.STATUS_RESULTS_DIRECTORY:
            self.res_dir = f"{settings.STATUS_RESULTS_DIRECTORY}"
        else:
            self.res_dir = f"{testcase.TestCase.dir_results}/kubernetes-status"

        if settings.K8S_CONFIG:
            config.load_kube_config(config_file=settings.K8S_CONFIG)
        else:
            config.load_kube_config()

        self.core = client.CoreV1Api()
        self.batch = client.BatchV1Api()
        self.app = client.AppsV1Api()
        self.networking = client.NetworkingV1Api()

        self.__logger.debug("namespace status init started")
        self.pods = []
        self.services = []
        self.jobs = []
        self.deployments = []
        self.replicasets =[]
        self.statefulsets = []
        self.daemonsets = []
        self.pvcs = []
        self.configmaps = []
        self.secrets = []
        self.ingresses = []
        self.details = {}

    @property
    def description(self) -> str:
        """Step description."""
        return "Check status of all k8s resources in the selected namespace."

    @property
    def component(self) -> str:
        """Component name."""
        return "ALL"

    @BaseStep.store_state
    def execute(self):
        """Check status of all k8s resources in the selected namespace.

        Use settings values:
         - K8S_ONAP_NAMESPACE.

        """
        super().execute()
        if settings.STORE_ARTIFACTS:
            os.makedirs(self.res_dir, exist_ok=True)
        self.__logger.debug("start test")
        try:
            self.k8s_pods = self.core.list_namespaced_pod(NAMESPACE).items
            self.__logger.info("%4s Pods in the namespace", len(self.k8s_pods))

            self.k8s_jobs = self.batch.list_namespaced_job(NAMESPACE).items
            self.__logger.info("%4s Jobs in the namespace", len(self.k8s_jobs))

            self.k8s_deployments = self.app.list_namespaced_deployment(
                NAMESPACE).items
            self.__logger.info("%4s Deployments in the namespace",
                               len(self.k8s_deployments))

            self.k8s_replicasets = self.app.list_namespaced_replica_set(
                NAMESPACE).items
            self.__logger.info("%4s Replicasets in the namespace",
                               len(self.k8s_replicasets))

            self.k8s_statefulsets = self.app.list_namespaced_stateful_set(
                NAMESPACE).items
            self.__logger.info("%4s StatefulSets in the namespace",
                               len(self.k8s_statefulsets))

            self.k8s_daemonsets = self.app.list_namespaced_daemon_set(
                NAMESPACE).items
            self.__logger.info("%4s DaemonSets in the namespace",
                               len(self.k8s_daemonsets))

            self.k8s_services = self.core.list_namespaced_service(
                NAMESPACE).items
            self.__logger.info("%4s Services in the namespace",
                               len(self.k8s_services))

            self.k8s_pvcs = self.core.list_namespaced_persistent_volume_claim(
                NAMESPACE).items
            self.__logger.info("%4s PVCs in the namespace", len(self.pvcs))

            self.k8s_configmaps = self.core.list_namespaced_config_map(
                NAMESPACE).items
            self.__logger.info("%4s ConfigMaps in the namespace",
                               len(self.configmaps))

            self.k8s_secrets = self.core.list_namespaced_secret(
                NAMESPACE).items
            self.__logger.info("%4s Secrets in the namespace",
                               len(self.secrets))

            self.k8s_ingresses = self.networking.list_namespaced_ingress(
                NAMESPACE).items
            self.__logger.info("%4s Ingresses in the namespace",
                               len(self.ingresses))
        except (ConnectionRefusedError, MaxRetryError, NewConnectionError):
            self.__logger.error("namespace status test failed.")
            self.__logger.error("cannot connect to Kubernetes.")
            return testcase.TestCase.EX_TESTCASE_FAILED

        self.failing_statefulsets = []
        self.failing_jobs = []
        self.failing_deployments = []
        self.failing_replicasets = []
        self.failing_daemonsets = []
        self.failing_pvcs = []
        self.failing = False

        self.jinja_env = Environment(autoescape=select_autoescape(['html']),
                                     loader=PackageLoader('onaptests.templates','status'))
        self.parse_services()
        jobs_pods = self.parse_jobs()
        self.parse_pods(excluded_pods=jobs_pods)
        self.parse_deployments()
        self.parse_replicasets()
        self.parse_statefulsets()
        self.parse_daemonsets()
        self.parse_pvcs()
        self.parse_configmaps()
        self.parse_secrets()
        self.parse_ingresses()
        self.parse_versions()
        if settings.STORE_ARTIFACTS:
            self.jinja_env.get_template('index.html.j2').stream(
                ns=self,
                delta=delta).dump('{}/index.html'.format(self.res_dir))
            self.jinja_env.get_template('raw_output.txt.j2').stream(
                ns=self, namespace=NAMESPACE).dump('{}/onap-k8s.log'.format(
                    self.res_dir))

        if len(self.jobs) > 0:
            self.details['jobs'] = {
                'number': len(self.jobs),
                'number_failing': len(self.failing_jobs),
                'failing': self.map_by_name(self.failing_jobs)
            }
        if len(self.deployments) > 0:
            self.details['deployments'] = {
                'number': len(self.deployments),
                'number_failing': len(self.failing_deployments),
                'failing': self.map_by_name(self.failing_deployments)
            }
        if len(self.replicasets) > 0:
            self.details['replicasets'] = {
                'number': len(self.replicasets),
                'number_failing': len(self.failing_replicasets),
                'failing': self.map_by_name(self.failing_replicasets)
            }
        if len(self.statefulsets) > 0:
            self.details['statefulsets'] = {
                'number': len(self.statefulsets),
                'number_failing': len(self.failing_statefulsets),
                'failing': self.map_by_name(self.failing_statefulsets)
            }
        if len(self.daemonsets) > 0:
            self.details['daemonsets'] = {
                'number': len(self.daemonsets),
                'number_failing': len(self.failing_daemonsets),
                'failing': self.map_by_name(self.failing_daemonsets)
            }
        if len(self.pvcs) > 0:
            self.details['pvcs'] = {
                'number': len(self.pvcs),
                'number_failing': len(self.failing_pvcs),
                'failing': self.map_by_name(self.failing_pvcs)
            }
        if self.failing:
            self.__logger.error("namespace status test failed.")
            self.__logger.error("number of errored Jobs: %s",
                                len(self.failing_jobs))
            self.__logger.error("number of errored Deployments: %s",
                                len(self.failing_deployments))
            self.__logger.error("number of errored Replicasets: %s",
                                len(self.failing_replicasets))
            self.__logger.error("number of errored StatefulSets: %s",
                                len(self.failing_statefulsets))
            self.__logger.error("number of errored DaemonSets: %s",
                                len(self.failing_daemonsets))
            self.__logger.error("number of errored PVCs: %s",
                                len(self.failing_pvcs))
            raise StatusCheckException

    def parse_pods(self, excluded_pods=None):
        """Parse the pods status."""
        self.__logger.info("%4s pods to parse", len(self.k8s_pods))
        for k8s in self.k8s_pods:
            pod = Pod(k8s=k8s)

            if excluded_pods and pod in excluded_pods:
                continue

            if k8s.status.init_container_statuses:
                for k8s_container in k8s.status.init_container_statuses:
                    pod.runned_init_containers += self.parse_container(
                        pod, k8s_container, init=True)
            if k8s.status.container_statuses:
                for k8s_container in k8s.status.container_statuses:
                    pod.running_containers += self.parse_container(
                        pod, k8s_container)
            pod.events = self.core.list_namespaced_event(
                NAMESPACE,
                field_selector="involvedObject.name={}".format(pod.name)).items
            if settings.STORE_ARTIFACTS:
                self.jinja_env.get_template('pod.html.j2').stream(pod=pod).dump(
                    '{}/pod-{}.html'.format(self.res_dir, pod.name))
                if any(waiver_elt in pod.name for waiver_elt in WAIVER_LIST):
                    self.__logger.warn("Waiver pattern found in pod, exclude %s", pod.name)
                else:
                    self.pods.append(pod)

    def parse_container(self, pod, k8s_container, init=False):
        """Get the logs of a container."""
        logs = ""
        old_logs = ""
        prefix = ""
        containers_list = pod.containers
        container = Container(name=k8s_container.name)
        container.restart_count = k8s_container.restart_count
        container.set_status(k8s_container.state)
        container.ready = k8s_container.ready
        container.image = k8s_container.image
        if init:
            prefix = "init "
            containers_list = pod.init_containers
            if container.restart_count > pod.init_restart_count:
                pod.init_restart_count = container.restart_count
            if not container.ready:
                pod.init_done = False
        else:
            if container.restart_count > pod.restart_count:
                pod.restart_count = container.restart_count

        try:
            log_files = {}
            logs = ""
            try:
                logs = self.core.read_namespaced_pod_log(
                    pod.name,
                    NAMESPACE,
                    container=container.name,
                    limit_bytes=MAX_LOG_BYTES,
                )
            except UnicodeDecodeError:
                logs= "{0} has an unicode decode error...".format(pod.name)
                self.__logger.error(
                    "{0} has an unicode decode error in the logs...", pod.name,
                )
            if settings.STORE_ARTIFACTS:
                with open(
                        "{}/pod-{}-{}.log".format(self.res_dir,
                                                pod.name, container.name),
                        'w') as log_result:
                    log_result.write(logs)
            if (not container.ready) and container.restart_count > 0:
                old_logs = self.core.read_namespaced_pod_log(
                    pod.name,
                    NAMESPACE,
                    container=container.name,
                    previous=True)
                if settings.STORE_ARTIFACTS:
                    with open(
                            "{}/pod-{}-{}.old.log".format(self.res_dir,
                                                        pod.name,
                                                        container.name),
                            'w') as log_result:
                        log_result.write(old_logs)
            if (container.name in FULL_LOGS_CONTAINERS):
                logs = self.core.read_namespaced_pod_log(
                    pod.name, NAMESPACE, container=container.name)
                if settings.STORE_ARTIFACTS:
                    with open(
                            "{}/pod-{}-{}.log".format(self.res_dir,
                                                    pod.name, container.name),
                            'w') as log_result:
                        log_result.write(logs)
            if (container.name in SPECIFIC_LOGS_CONTAINERS):
                for log_file in SPECIFIC_LOGS_CONTAINERS[container.name]:
                    exec_command = ['/bin/sh', '-c', "cat {}".format(log_file)]
                    log_files[log_file] = stream(
                        self.core.connect_get_namespaced_pod_exec,
                        pod.name,
                        NAMESPACE,
                        container=container.name,
                        command=exec_command,
                        stderr=True,
                        stdin=False,
                        stdout=True,
                        tty=False)
                    log_file_slug = log_file.split('.')[0].split('/')[-1]
                    with open(
                            "{}/pod-{}-{}-{}.log".format(
                                self.res_dir, pod.name,
                                container.name, log_file_slug),
                            'w') as log_result:
                        log_result.write(log_files[log_file])
        except client.rest.ApiException as exc:
            self.__logger.warning("%scontainer %s of pod %s has an exception: %s",
                               prefix, container.name, pod.name, exc.reason)
        if settings.STORE_ARTIFACTS:
            self.jinja_env.get_template('container_log.html.j2').stream(
                container=container,
                pod_name=pod.name,
                logs=logs,
                old_logs=old_logs,
                log_files=log_files).dump('{}/pod-{}-{}-logs.html'.format(
                    self.res_dir, pod.name, container.name))
        if any(waiver_elt in container.name for waiver_elt in WAIVER_LIST):
            self.__logger.warn(
                "Waiver pattern found in container, exclude %s", container.name)
        else:
            containers_list.append(container)
            if k8s_container.ready:
                return 1
        return 0

    def parse_services(self):
        """Parse the services."""
        self.__logger.info("%4s services to parse", len(self.k8s_services))
        for k8s in self.k8s_services:
            service = Service(k8s=k8s)

            (service.pods,
             service.failed_pods) = self._find_child_pods(k8s.spec.selector)

            if settings.STORE_ARTIFACTS:
                self.jinja_env.get_template('service.html.j2').stream(
                    service=service).dump('{}/service-{}.html'.format(
                        self.res_dir, service.name))
                self.services.append(service)

    def parse_jobs(self):
        """Parse the jobs.
        Return a list of Pods that were created to perform jobs.
        """
        self.__logger.info("%4s jobs to parse", len(self.k8s_jobs))
        jobs_pods = []
        for i in range(len(self.k8s_jobs)):
            k8s = self.k8s_jobs[i]
            job = Job(k8s=k8s)
            job_pods = []

            if k8s.spec.selector and k8s.spec.selector.match_labels:
                (job.pods, job.failed_pods) = self._find_child_pods(
                    k8s.spec.selector.match_labels)
                job_pods += job.pods
            field_selector = "involvedObject.name={}".format(job.name)
            field_selector += ",involvedObject.kind=Job"
            job.events = self.core.list_namespaced_event(
                NAMESPACE,
                field_selector=field_selector).items

            if settings.STORE_ARTIFACTS:
                self.jinja_env.get_template('job.html.j2').stream(job=job).dump(
                    '{}/job-{}.html'.format(self.res_dir, job.name))

            # timemout job
            if not k8s.status.completion_time:
                self.__logger.warning("a Job is in error: {}".format(job.name))
                if any(
                    waiver_elt not in job.name for waiver_elt in WAIVER_LIST):
                    self.failing_jobs.append(job)
                    self.failing = True
            # completed job
            if any(waiver_elt not in job.name for waiver_elt in WAIVER_LIST):
                self.jobs.append(job)
            jobs_pods += job_pods
        return jobs_pods

    def parse_deployments(self):
        """Parse the deployments."""
        self.__logger.info("%4s deployments to parse",
                           len(self.k8s_deployments))
        for i in range(len(self.k8s_deployments)):
            k8s = self.k8s_deployments[i]
            deployment = Deployment(k8s=k8s)

            if k8s.spec.selector and k8s.spec.selector.match_labels:
                (deployment.pods,
                 deployment.failed_pods) = self._find_child_pods(
                     k8s.spec.selector.match_labels)
            field_selector = "involvedObject.name={}".format(deployment.name)
            field_selector += ",involvedObject.kind=Deployment"
            deployment.events = self.core.list_namespaced_event(
                NAMESPACE,
                field_selector=field_selector).items

            if settings.STORE_ARTIFACTS:
                self.jinja_env.get_template('deployment.html.j2').stream(
                    deployment=deployment).dump('{}/deployment-{}.html'.format(
                        self.res_dir, deployment.name))

            if k8s.status.unavailable_replicas:
                self.__logger.warning("a Deployment is in error: {}".format(deployment.name))
                self.failing_deployments.append(deployment)
                self.failing = True

            self.deployments.append(deployment)

    def parse_replicasets(self):
        """Parse the replicasets."""
        self.__logger.info("%4s replicasets to parse",
                           len(self.k8s_replicasets))
        for i in range(len(self.k8s_replicasets)):
            k8s = self.k8s_replicasets[i]
            replicaset = ReplicaSet(k8s=k8s)

            if k8s.spec.selector and k8s.spec.selector.match_labels:
                (replicaset.pods,
                 replicaset.failed_pods) = self._find_child_pods(
                     k8s.spec.selector.match_labels)
            field_selector = "involvedObject.name={}".format(replicaset.name)
            field_selector += ",involvedObject.kind=ReplicaSet"
            replicaset.events = self.core.list_namespaced_event(
                NAMESPACE,
                field_selector=field_selector).items

            if settings.STORE_ARTIFACTS:
                self.jinja_env.get_template('replicaset.html.j2').stream(
                    replicaset=replicaset).dump('{}/replicaset-{}.html'.format(
                        self.res_dir, replicaset.name))

            if (not k8s.status.ready_replicas 
                or (k8s.status.ready_replicas < k8s.status.replicas)):
                self.__logger.warning("a ReplicaSet is in error: {}".format(replicaset.name))
                self.failing_replicasets.append(replicaset)
                self.failing = True

            self.replicasets.append(replicaset)

    def parse_statefulsets(self):
        """Parse the statefulsets."""
        self.__logger.info("%4s statefulsets to parse",
                           len(self.k8s_statefulsets))
        for i in range(len(self.k8s_statefulsets)):
            k8s = self.k8s_statefulsets[i]
            statefulset = StatefulSet(k8s=k8s)

            if k8s.spec.selector and k8s.spec.selector.match_labels:
                (statefulset.pods,
                 statefulset.failed_pods) = self._find_child_pods(
                     k8s.spec.selector.match_labels)
            field_selector = "involvedObject.name={}".format(statefulset.name)
            field_selector += ",involvedObject.kind=StatefulSet"
            statefulset.events = self.core.list_namespaced_event(
                NAMESPACE,
                field_selector=field_selector).items

            if settings.STORE_ARTIFACTS:
                self.jinja_env.get_template('statefulset.html.j2').stream(
                    statefulset=statefulset).dump('{}/statefulset-{}.html'.format(
                        self.res_dir, statefulset.name))

            if ((not k8s.status.ready_replicas)
                    or (k8s.status.ready_replicas < k8s.status.replicas)):
                self.__logger.warning("a StatefulSet is in error: {}".format(statefulset.name))
                self.failing_statefulsets.append(statefulset)
                self.failing = True

            self.statefulsets.append(statefulset)

    def parse_daemonsets(self):
        """Parse the daemonsets."""
        self.__logger.info("%4s daemonsets to parse", len(self.k8s_daemonsets))
        for i in range(len(self.k8s_daemonsets)):
            k8s = self.k8s_daemonsets[i]
            daemonset = DaemonSet(k8s=k8s)

            if k8s.spec.selector and k8s.spec.selector.match_labels:
                (daemonset.pods,
                 daemonset.failed_pods) = self._find_child_pods(
                     k8s.spec.selector.match_labels)
            field_selector = "involvedObject.name={}".format(daemonset.name)
            field_selector += ",involvedObject.kind=DaemonSet"
            daemonset.events = self.core.list_namespaced_event(
                NAMESPACE,
                field_selector=field_selector).items

            if settings.STORE_ARTIFACTS:
                self.jinja_env.get_template('daemonset.html.j2').stream(
                    daemonset=daemonset).dump('{}/daemonset-{}.html'.format(
                        self.res_dir, daemonset.name))

            if (k8s.status.number_ready < k8s.status.desired_number_scheduled):
                self.__logger.warning("a DaemonSet is in error: {}".format(daemonset.name))
                self.failing_daemonsets.append(daemonset)
                self.failing = True

            self.daemonsets.append(daemonset)

    def parse_pvcs(self):
        """Parse the persistent volume claims."""
        self.__logger.info("%4s pvcs to parse", len(self.k8s_pvcs))
        for k8s in self.k8s_pvcs:
            pvc = Pvc(k8s=k8s)
            field_selector = f"involvedObject.name={pvc.name},involvedObject.kind=PersistentVolumeClaim"
            pvc.events = self.core.list_namespaced_event(
                NAMESPACE,
                field_selector=field_selector).items

            if k8s.status.phase != "Bound":
                self.__logger.warning("a PVC is in error: {}".format(pvc.name))
                self.failing_pvcs.append(pvc)
                self.failing = True

            self.pvcs.append(pvc)

    def parse_configmaps(self):
        """Parse the config maps."""
        self.__logger.info("%4s config maps to parse",
                           len(self.k8s_configmaps))
        for k8s in self.k8s_configmaps:
            configmap = ConfigMap(k8s=k8s)
            self.configmaps.append(configmap)

    def parse_secrets(self):
        """Parse the secrets."""
        self.__logger.info("%4s secrets to parse", len(self.k8s_secrets))
        for k8s in self.k8s_secrets:
            secret = Secret(k8s=k8s)
            self.secrets.append(secret)

    def parse_ingresses(self):
        """Parse the ingresses."""
        self.__logger.info("%4s ingresses to parse", len(self.k8s_ingresses))
        for k8s in self.k8s_secrets:
            ingress = Ingress(k8s=k8s)
            self.ingresses.append(ingress)

    def parse_versions(self):
        """Parse the versions of the pods."""
        self.__logger.info("%4s pods to parse", len(self.k8s_pods))
        pod_versions = []
        containers = {}
        for pod in self.k8s_pods:
            pod_component = pod.metadata.name
            if 'app' in pod.metadata.labels:
                pod_component = pod.metadata.labels['app']
            else:
                if 'app.kubernetes.io/name' in pod.metadata.labels:
                    pod_component = pod.metadata.labels[
                        'app.kubernetes.io/name']
                else:
                    self.__logger.error("pod %s has no 'app' or 'app.kubernetes.io/name' in metadata: %s", pod_component, pod.metadata.labels)

            # looks for docker version
            for container in pod.spec.containers:
                pod_version = {}
                pod_container_version = container.image.rsplit(":", 1)
                pod_container_image = pod_container_version[0]
                pod_container_tag = "latest"
                if len(pod_container_version) > 1:
                    pod_container_tag = pod_container_version[1]

                pod_version.update({
                    'container': container.name,
                    'component': pod_component,
                    'image': pod_container_image,
                    'version': pod_container_tag
                })
                pod_versions.append(pod_version)

                search_rule = "^(?P<source>[^/]*)/*(?P<container>[^:]*):*(?P<version>.*)$"
                search = re.search(search_rule, container.image)
                name = "{}/{}".format(search.group('source'),
                                      search.group('container'))
                version = search.group('version')
                if name[-1] == '/':
                    name = name[0:-1]
                source = "default"
                if search.group('source') in DOCKER_REPOSITORIES:
                    source = search.group('source')
                    name = search.group('container')
                container_search_rule = "^library/(?P<real_container>[^:]*)$"
                container_search = re.search(container_search_rule, name)
                if container_search:
                    name = container_search.group('real_container')
                for common_component in GENERIC_NAMES.keys():
                    if name in GENERIC_NAMES[common_component]:
                        version = "{}:{}".format(name, version)
                        name = common_component
                        break

                repository = DOCKER_REPOSITORIES_NICKNAMES[source]
                if name in containers:
                    if version in containers[name]['versions']:
                        if not (pod_component in containers[name]['versions']
                                [version]['components']):
                            containers[name]['versions'][version][
                                'components'].append(pod_component)
                            containers[name]['number_components'] += 1
                        if not (repository in containers[name]['versions']
                                [version]['repositories']):
                            containers[name]['versions'][version][
                                'repositories'].append(repository)
                    else:
                        containers[name]['versions'][version] = {
                            'repositories': [repository],
                            'components': [pod_component]
                        }
                        containers[name]['number_components'] += 1
                else:
                    containers[name] = {
                        'versions': {
                            version: {
                                'repositories': [repository],
                                'components': [pod_component]
                            }
                        },
                        'number_components': 1
                    }

        if settings.STORE_ARTIFACTS:
            self.jinja_env.get_template('version.html.j2').stream(
                pod_versions=pod_versions).dump('{}/versions.html'.format(
                    self.res_dir))
            self.jinja_env.get_template('container_versions.html.j2').stream(
                containers=containers).dump('{}/container_versions.html'.format(
                    self.res_dir))
        # create a json file for version tracking
        with open(self.res_dir + "/onap_versions.json", "w") as write_file:
            json.dump(pod_versions, write_file)

    def _find_child_pods(self, selector):
        pods_list = []
        failed_pods = 0
        if selector:
            raw_selector = ''
            for key, value in selector.items():
                raw_selector += key + '=' + value + ','
            raw_selector = raw_selector[:-1]
            pods = self.core.list_namespaced_pod(
                NAMESPACE, label_selector=raw_selector).items
            for pod in pods:
                for known_pod in self.pods:
                    if known_pod.name == pod.metadata.name:
                        pods_list.append(known_pod)
                        if not known_pod.ready():
                            failed_pods += 1
        return (pods_list, failed_pods)

    def map_by_name(self, resources):
        return list(map(lambda resource: resource.name, resources))
