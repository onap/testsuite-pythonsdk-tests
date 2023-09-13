#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import os
import re
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape
from kubernetes import client, config
from kubernetes.stream import stream
from natural.date import delta
from urllib3.exceptions import MaxRetryError, NewConnectionError
from xtesting.core import testcase

from onapsdk.configuration import settings
from onaptests.utils.exceptions import StatusCheckException

from ..base import BaseStep
from .resources import (ConfigMap, Container, DaemonSet, Deployment, Ingress,
                        Job, Pod, Pvc, ReplicaSet, Secret, Service,
                        StatefulSet)

X = settings.K8S_ONAP_NAMESPACE


class CheckK8sResourcesStep(BaseStep):

    __logger = logging.getLogger(__name__)

    def __init__(self, namespace: str, resource_type: str, break_on_error=False):
        """Init CheckK8sResourcesStep."""
        super().__init__(cleanup=BaseStep.HAS_NO_CLEANUP, break_on_error=break_on_error)
        self.core = client.CoreV1Api()
        self.batch = client.BatchV1Api()
        self.app = client.AppsV1Api()
        self.networking = client.NetworkingV1Api()
        self.namespace = namespace

        if settings.STATUS_RESULTS_DIRECTORY:
            self.res_dir = f"{settings.STATUS_RESULTS_DIRECTORY}"
        else:
            self.res_dir = f"{testcase.TestCase.dir_results}/kubernetes-status"

        if not self.is_primary:
            self.res_dir = f"{self.res_dir}/{self.namespace}"

        self.failing = False
        self.resource_type = resource_type
        self.k8s_resources = []
        self.all_resources = []
        self.failing_resources = []
        self.jinja_env = Environment(autoescape=select_autoescape(['html']),
                                     loader=PackageLoader('onaptests.templates', 'status'))

    @property
    def component(self) -> str:
        """Component name."""
        return "ALL"

    @property
    def description(self) -> str:
        """Step description."""
        return f"Check status of all k8s {self.resource_type}s in the {self.namespace} namespace."

    @property
    def is_primary(self) -> bool:
        """Does step analyses primary namespace."""
        return self.namespace == settings.K8S_ONAP_NAMESPACE

    def _init_resources(self):
        if self.resource_type != "":
            self.__logger.debug(f"Loading all k8s {self.resource_type}s"
                                " in the {NAMESPACE} namespace")

    def _parse_resources(self):
        """Parse the resources."""
        return []

    def _add_failing_resource(self, resource):
        if (resource.labels and settings.EXCLUDED_LABELS
                and (resource.labels.keys() and settings.EXCLUDED_LABELS.keys())):
            for label in resource.labels.items():
                for waived_label in settings.EXCLUDED_LABELS.items():
                    if label[0] in waived_label[0] and label[1] in waived_label[1]:
                        return
        self.__logger.warning("a {} is in error: {}".format(self.resource_type, resource.name))
        self.failing_resources.append(resource)
        self.failing = True

    def execute(self):
        super().execute()
        os.makedirs(self.res_dir, exist_ok=True)
        try:
            self._init_resources()
            if len(self.k8s_resources) > 0:
                self.__logger.info("%4s %ss in the namespace",
                                   len(self.k8s_resources),
                                   self.resource_type)
                self._parse_resources()
                self.__logger.info("%4s %ss parsed, %s failing",
                                   len(self.all_resources),
                                   self.resource_type,
                                   len(self.failing_resources))
                if self.failing:
                    raise StatusCheckException(f"{self.resource_type} test failed")
        except (ConnectionRefusedError, MaxRetryError, NewConnectionError) as e:
            self.__logger.error("Test of k8s %ss failed.", self.resource_type)
            self.__logger.error("Cannot connect to Kubernetes.")
            raise StatusCheckException from e


class CheckBasicK8sResourcesStep(CheckK8sResourcesStep):

    def __init__(self, namespace, resource_type: str, k8s_res_class):
        """Init CheckBasicK8sResourcesStep."""
        super().__init__(namespace=namespace, resource_type=resource_type)
        self.k8s_res_class = k8s_res_class

    def _parse_resources(self):
        """Parse simple k8s resources."""
        super()._parse_resources()
        for k8s in self.k8s_resources:
            resource = self.k8s_res_class(k8s=k8s)
            self.all_resources.append(resource)

    @BaseStep.store_state
    def execute(self):
        super().execute()


class CheckK8sConfigMapsStep(CheckBasicK8sResourcesStep):

    def __init__(self, namespace):
        """Init CheckK8sConfigMapsStep."""
        super().__init__(namespace=namespace, resource_type="configmap", k8s_res_class=ConfigMap)

    def _init_resources(self):
        super()._init_resources()
        self.k8s_resources = self.core.list_namespaced_config_map(self.namespace).items


class CheckK8sSecretsStep(CheckBasicK8sResourcesStep):

    def __init__(self, namespace):
        """Init CheckK8sSecretsStep."""
        super().__init__(namespace=namespace, resource_type="secret", k8s_res_class=Secret)

    def _init_resources(self):
        super()._init_resources()
        self.k8s_resources = self.core.list_namespaced_secret(self.namespace).items


class CheckK8sIngressesStep(CheckBasicK8sResourcesStep):

    def __init__(self, namespace):
        """Init CheckK8sIngressesStep."""
        super().__init__(namespace=namespace, resource_type="ingress", k8s_res_class=Ingress)

    def _init_resources(self):
        super()._init_resources()
        self.k8s_resources = self.networking.list_namespaced_ingress(self.namespace).items


class CheckK8sPvcsStep(CheckK8sResourcesStep):

    def __init__(self, namespace):
        """Init CheckK8sPvcsStep."""
        super().__init__(namespace=namespace, resource_type="pvc")

    def _init_resources(self):
        super()._init_resources()
        self.k8s_resources = self.core.list_namespaced_persistent_volume_claim(self.namespace).items

    def _parse_resources(self):
        """Parse the jobs.
        Return a list of Pods that were created to perform jobs.
        """
        super()._parse_resources()
        for k8s in self.k8s_resources:
            pvc = Pvc(k8s=k8s)
            field_selector = (f"involvedObject.name={pvc.name},"
                              "involvedObject.kind=PersistentVolumeClaim")
            pvc.events = self.core.list_namespaced_event(
                self.namespace,
                field_selector=field_selector).items

            if k8s.status.phase != "Bound":
                self._add_failing_resource(pvc)
            self.all_resources.append(pvc)

    @BaseStep.store_state
    def execute(self):
        super().execute()


class CheckK8sResourcesUsingPodsStep(CheckK8sResourcesStep):

    def __init__(self, namespace, resource_type: str, pods_source):
        """Init CheckK8sResourcesUsingPodsStep."""
        super().__init__(namespace=namespace, resource_type=resource_type)
        self.pods_source = pods_source

    def _get_used_pods(self):
        pods = []
        if self.pods_source is not None:
            pods = self.pods_source.all_resources
        return pods

    def _find_child_pods(self, selector):
        pods_used = self._get_used_pods()
        pods_list = []
        failed_pods = 0
        if selector:
            raw_selector = ''
            for key, value in selector.items():
                raw_selector += key + '=' + value + ','
            raw_selector = raw_selector[:-1]
            pods = self.core.list_namespaced_pod(
                self.namespace, label_selector=raw_selector).items
            for pod in pods:
                for known_pod in pods_used:
                    if known_pod.name == pod.metadata.name:
                        pods_list.append(known_pod)
                        if not known_pod.ready():
                            failed_pods += 1
        return (pods_list, failed_pods)

    @BaseStep.store_state
    def execute(self):
        super().execute()


class CheckK8sJobsStep(CheckK8sResourcesUsingPodsStep):

    def __init__(self, namespace):
        """Init CheckK8sJobsStep."""
        super().__init__(namespace=namespace, resource_type="job", pods_source=None)

    def _init_resources(self):
        super()._init_resources()
        self.k8s_resources = self.batch.list_namespaced_job(self.namespace).items

    def _parse_resources(self):
        """Parse the jobs.
        Return a list of Pods that were created to perform jobs.
        """
        super()._parse_resources()
        jobs_pods = []
        for k8s in self.k8s_resources:
            job = Job(k8s=k8s)
            job_pods = []

            if k8s.spec.selector and k8s.spec.selector.match_labels:
                (job.pods, job.failed_pods) = self._find_child_pods(
                    k8s.spec.selector.match_labels)
                job_pods += job.pods
            field_selector = "involvedObject.name={}".format(job.name)
            field_selector += ",involvedObject.kind=Job"
            job.events = self.core.list_namespaced_event(
                self.namespace,
                field_selector=field_selector).items

            self.jinja_env.get_template('job.html.j2').stream(job=job).dump(
                '{}/job-{}.html'.format(self.res_dir, job.name))

            # timemout job
            if not k8s.status.completion_time:
                if any(waiver_elt not in job.name for waiver_elt in settings.WAIVER_LIST):
                    self._add_failing_resource(job)
            # completed job
            if any(waiver_elt not in job.name for waiver_elt in settings.WAIVER_LIST):
                self.all_resources.append(job)
            jobs_pods += job_pods


class CheckK8sPodsStep(CheckK8sResourcesUsingPodsStep):

    __logger = logging.getLogger(__name__)

    def __init__(self, namespace, pods):
        """Init CheckK8sPodsStep."""
        super().__init__(namespace=namespace, resource_type="pod", pods_source=pods)

    def _init_resources(self):
        super()._init_resources()
        self.k8s_resources = self.core.list_namespaced_pod(self.namespace).items

    def _parse_resources(self):  # noqa
        """Parse the pods."""
        super()._parse_resources()
        excluded_pods = self._get_used_pods()
        pod_versions = []
        containers = {}
        for k8s in self.k8s_resources:
            pod = Pod(k8s=k8s)

            # check version firstly
            if settings.CHECK_POD_VERSIONS:
                pod_component = k8s.metadata.name
                pod_component_from_label = None
                if hasattr(k8s.metadata, "labels") and k8s.metadata.labels is not None:
                    if 'app' in k8s.metadata.labels:
                        pod_component_from_label = k8s.metadata.labels['app']
                    else:
                        if 'app.kubernetes.io/name' in k8s.metadata.labels:
                            pod_component_from_label = k8s.metadata.labels[
                                'app.kubernetes.io/name']
                if pod_component_from_label is None:
                    self.__logger.error("pod %s has no 'app' or 'app.kubernetes.io/name' "
                                        "in metadata: %s", pod_component, k8s.metadata.labels)
                else:
                    pod_component = pod_component_from_label

                # looks for docker version
                for container in k8s.spec.containers:
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
                    if search.group('source') in settings.DOCKER_REPOSITORIES:
                        source = search.group('source')
                        name = search.group('container')
                    container_search_rule = "^library/(?P<real_container>[^:]*)$"
                    container_search = re.search(container_search_rule, name)
                    if container_search:
                        name = container_search.group('real_container')
                    for common_component in settings.GENERIC_NAMES.keys():
                        if name in settings.GENERIC_NAMES[common_component]:
                            version = "{}:{}".format(name, version)
                            name = common_component
                            break

                    repository = settings.DOCKER_REPOSITORIES_NICKNAMES[source]
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
            # pod version check end
            if excluded_pods and pod in excluded_pods:
                continue

            if k8s.status.init_container_statuses:
                for k8s_container in k8s.status.init_container_statuses:
                    pod.runned_init_containers += self._parse_container(
                        pod, k8s_container, init=True)
            if k8s.status.container_statuses:
                for k8s_container in k8s.status.container_statuses:
                    pod.running_containers += self._parse_container(
                        pod, k8s_container)
            pod.events = self.core.list_namespaced_event(
                self.namespace,
                field_selector="involvedObject.name={}".format(pod.name)).items
            self.jinja_env.get_template('pod.html.j2').stream(pod=pod).dump(
                '{}/pod-{}.html'.format(self.res_dir, pod.name))
            if any(waiver_elt in pod.name for waiver_elt in settings.WAIVER_LIST):
                self.__logger.warn("Waiver pattern found in pod, exclude %s", pod.name)
            else:
                self.all_resources.append(pod)

        if settings.CHECK_POD_VERSIONS:
            self.jinja_env.get_template('version.html.j2').stream(
                pod_versions=pod_versions).dump('{}/versions.html'.format(
                    self.res_dir))
            self.jinja_env.get_template('container_versions.html.j2').stream(
                containers=containers).dump('{}/container_versions.html'.format(
                    self.res_dir))
            # create a json file for version tracking
            with open(self.res_dir + "/onap_versions.json", "w") as write_file:
                json.dump(pod_versions, write_file)

    def _get_container_logs(self, pod, container, full=True, previous=False):
        logs = ""
        limit_bytes = settings.MAX_LOG_BYTES
        if full:
            limit_bytes = settings.UNLIMITED_LOG_BYTES
        try:
            logs = self.core.read_namespaced_pod_log(
                pod.name,
                self.namespace,
                container=container.name,
                limit_bytes=limit_bytes,
                previous=previous
            )
        except UnicodeDecodeError:
            logs = "{0} has an unicode decode error...".format(pod.name)
            self.__logger.error(
                "{0} has an unicode decode error in the logs...", pod.name,
            )
        return logs

    def _parse_container(self, pod, k8s_container, init=False):  # noqa
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
        if settings.STORE_ARTIFACTS:
            try:
                log_files = {}
                logs = self._get_container_logs(pod=pod, container=container, full=False)
                with open(
                        "{}/pod-{}-{}.log".format(self.res_dir,
                                                  pod.name, container.name),
                        'w') as log_result:
                    log_result.write(logs)
                if (not container.ready) and container.restart_count > 0:
                    old_logs = self._get_container_logs(pod=pod, container=container,
                                                        previous=True)
                    with open(
                            "{}/pod-{}-{}.old.log".format(self.res_dir,
                                                          pod.name,
                                                          container.name),
                            'w') as log_result:
                        log_result.write(old_logs)
                if (container.name in settings.FULL_LOGS_CONTAINERS):
                    logs = self._get_container_logs(pod=pod, container=container)
                    with open(
                            "{}/pod-{}-{}.log".format(self.res_dir,
                                                      pod.name, container.name),
                            'w') as log_result:
                        log_result.write(logs)
                if (container.name in settings.SPECIFIC_LOGS_CONTAINERS):
                    for log_file in settings.SPECIFIC_LOGS_CONTAINERS[container.name]:
                        exec_command = ['/bin/sh', '-c', "cat {}".format(log_file)]
                        log_files[log_file] = stream(
                            self.core.connect_get_namespaced_pod_exec,
                            pod.name,
                            self.namespace,
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
            self.jinja_env.get_template('container_log.html.j2').stream(
                container=container,
                pod_name=pod.name,
                logs=logs,
                old_logs=old_logs,
                log_files=log_files).dump('{}/pod-{}-{}-logs.html'.format(
                    self.res_dir, pod.name, container.name))
        if any(waiver_elt in container.name for waiver_elt in settings.WAIVER_LIST):
            self.__logger.warn(
                "Waiver pattern found in container, exclude %s", container.name)
        else:
            containers_list.append(container)
            if k8s_container.ready:
                return 1
        return 0


class CheckK8sServicesStep(CheckK8sResourcesUsingPodsStep):

    def __init__(self, namespace, pods):
        """Init CheckK8sServicesStep."""
        super().__init__(namespace=namespace, resource_type="service", pods_source=pods)

    def _init_resources(self):
        super()._init_resources()
        self.k8s_resources = self.core.list_namespaced_service(self.namespace).items

    def _parse_resources(self):
        """Parse the services."""
        super()._parse_resources()
        for k8s in self.k8s_resources:
            service = Service(k8s=k8s)

            (service.pods,
             service.failed_pods) = self._find_child_pods(k8s.spec.selector)

            self.jinja_env.get_template('service.html.j2').stream(
                service=service).dump('{}/service-{}.html'.format(
                    self.res_dir, service.name))
            self.all_resources.append(service)


class CheckK8sDeploymentsStep(CheckK8sResourcesUsingPodsStep):

    def __init__(self, namespace, pods):
        """Init CheckK8sDeploymentsStep."""
        super().__init__(namespace=namespace, resource_type="deployment", pods_source=pods)

    def _init_resources(self):
        super()._init_resources()
        self.k8s_resources = self.app.list_namespaced_deployment(self.namespace).items

    def _parse_resources(self):
        """Parse the deployments."""
        super()._parse_resources()
        for k8s in self.k8s_resources:
            deployment = Deployment(k8s=k8s)

            if settings.IGNORE_EMPTY_REPLICAS and k8s.spec.replicas == 0:
                continue
            if k8s.spec.selector and k8s.spec.selector.match_labels:
                (deployment.pods,
                 deployment.failed_pods) = self._find_child_pods(
                     k8s.spec.selector.match_labels)
            field_selector = "involvedObject.name={}".format(deployment.name)
            field_selector += ",involvedObject.kind=Deployment"
            deployment.events = self.core.list_namespaced_event(
                self.namespace,
                field_selector=field_selector).items

            self.jinja_env.get_template('deployment.html.j2').stream(
                deployment=deployment).dump('{}/deployment-{}.html'.format(
                    self.res_dir, deployment.name))

            if k8s.status.unavailable_replicas:
                self._add_failing_resource(deployment)

            self.all_resources.append(deployment)


class CheckK8sReplicaSetsStep(CheckK8sResourcesUsingPodsStep):

    def __init__(self, namespace, pods):
        """Init CheckK8sReplicaSetsStep."""
        super().__init__(namespace=namespace, resource_type="replicaset", pods_source=pods)

    def _init_resources(self):
        super()._init_resources()
        self.k8s_resources = self.app.list_namespaced_replica_set(self.namespace).items

    def _parse_resources(self):
        """Parse the replicasets."""
        super()._parse_resources()
        for k8s in self.k8s_resources:
            replicaset = ReplicaSet(k8s=k8s)

            if settings.IGNORE_EMPTY_REPLICAS and k8s.spec.replicas == 0:
                continue

            if k8s.spec.selector and k8s.spec.selector.match_labels:
                (replicaset.pods,
                 replicaset.failed_pods) = self._find_child_pods(
                     k8s.spec.selector.match_labels)
            field_selector = "involvedObject.name={}".format(replicaset.name)
            field_selector += ",involvedObject.kind=ReplicaSet"
            replicaset.events = self.core.list_namespaced_event(
                self.namespace,
                field_selector=field_selector).items

            self.jinja_env.get_template('replicaset.html.j2').stream(
                replicaset=replicaset).dump('{}/replicaset-{}.html'.format(
                    self.res_dir, replicaset.name))

            if (not k8s.status.ready_replicas or
                    (k8s.status.ready_replicas < k8s.status.replicas)):
                self._add_failing_resource(replicaset)

            self.all_resources.append(replicaset)


class CheckK8sStatefulSetsStep(CheckK8sResourcesUsingPodsStep):

    def __init__(self, namespace, pods):
        """Init CheckK8sStatefulSetsStep."""
        super().__init__(namespace=namespace, resource_type="statefulset", pods_source=pods)

    def _init_resources(self):
        super()._init_resources()
        self.k8s_resources = self.app.list_namespaced_stateful_set(self.namespace).items

    def _parse_resources(self):
        """Parse the statefulsets."""
        super()._parse_resources()
        for k8s in self.k8s_resources:
            statefulset = StatefulSet(k8s=k8s)

            if settings.IGNORE_EMPTY_REPLICAS and k8s.spec.replicas == 0:
                continue

            if k8s.spec.selector and k8s.spec.selector.match_labels:
                (statefulset.pods,
                 statefulset.failed_pods) = self._find_child_pods(
                     k8s.spec.selector.match_labels)
            field_selector = "involvedObject.name={}".format(statefulset.name)
            field_selector += ",involvedObject.kind=StatefulSet"
            statefulset.events = self.core.list_namespaced_event(
                self.namespace,
                field_selector=field_selector).items

            self.jinja_env.get_template('statefulset.html.j2').stream(
                statefulset=statefulset).dump('{}/statefulset-{}.html'.format(
                    self.res_dir, statefulset.name))

            if ((not k8s.status.ready_replicas)
                    or (k8s.status.ready_replicas < k8s.status.replicas)):
                self._add_failing_resource(statefulset)

            self.all_resources.append(statefulset)


class CheckK8sDaemonSetsStep(CheckK8sResourcesUsingPodsStep):

    def __init__(self, namespace, pods):
        """Init CheckK8sDaemonSetsStep."""
        super().__init__(namespace=namespace, resource_type="daemonset", pods_source=pods)

    def _init_resources(self):
        super()._init_resources()
        self.k8s_resources = self.app.list_namespaced_daemon_set(self.namespace).items

    def _parse_resources(self):
        """Parse the daemonsets."""
        super()._parse_resources()
        for k8s in self.k8s_resources:
            daemonset = DaemonSet(k8s=k8s)

            if settings.IGNORE_EMPTY_REPLICAS and k8s.spec.replicas == 0:
                continue

            if k8s.spec.selector and k8s.spec.selector.match_labels:
                (daemonset.pods,
                 daemonset.failed_pods) = self._find_child_pods(
                     k8s.spec.selector.match_labels)
            field_selector = "involvedObject.name={}".format(daemonset.name)
            field_selector += ",involvedObject.kind=DaemonSet"
            daemonset.events = self.core.list_namespaced_event(
                self.namespace,
                field_selector=field_selector).items

            self.jinja_env.get_template('daemonset.html.j2').stream(
                daemonset=daemonset).dump('{}/daemonset-{}.html'.format(
                    self.res_dir, daemonset.name))

            if (k8s.status.number_ready < k8s.status.desired_number_scheduled):
                self._add_failing_resource(daemonset)

            self.all_resources.append(daemonset)


class CheckNamespaceStatusStep(CheckK8sResourcesStep):
    """Check status of all k8s resources in the selected namespace."""

    __logger = logging.getLogger(__name__)

    def __init__(self):
        """Init CheckNamespaceStatusStep."""
        super().__init__(namespace=settings.K8S_ONAP_NAMESPACE, resource_type="")
        self.__logger.debug("K8s namespaces status test init started")
        if settings.IN_CLUSTER:
            config.load_incluster_config()
        else:
            config.load_kube_config(config_file=settings.K8S_CONFIG)
        for namespace in ([self.namespace] + settings.EXTRA_NAMESPACE_LIST):
            self._init_namespace_steps(namespace)

    def _init_namespace_steps(self, namespace):
        self.job_list_step = CheckK8sJobsStep(namespace)
        self.pod_list_step = CheckK8sPodsStep(namespace, self.job_list_step)
        self.service_list_step = CheckK8sServicesStep(namespace, self.pod_list_step)
        self.deployment_list_step = CheckK8sDeploymentsStep(namespace, self.pod_list_step)
        self.replicaset_list_step = CheckK8sReplicaSetsStep(namespace, self.pod_list_step)
        self.statefulset_list_step = CheckK8sStatefulSetsStep(namespace, self.pod_list_step)
        self.daemonset_list_step = CheckK8sDaemonSetsStep(namespace, self.pod_list_step)
        self.configmap_list_step = CheckK8sConfigMapsStep(namespace)
        self.secret_list_step = CheckK8sSecretsStep(namespace)
        self.ingress_list_step = CheckK8sIngressesStep(namespace)
        self.pvc_list_step = CheckK8sPvcsStep(namespace)
        self.add_step(self.job_list_step)
        self.add_step(self.pod_list_step)
        self.add_step(self.service_list_step)
        self.add_step(self.deployment_list_step)
        self.add_step(self.replicaset_list_step)
        self.add_step(self.statefulset_list_step)
        self.add_step(self.daemonset_list_step)
        self.add_step(self.configmap_list_step)
        self.add_step(self.secret_list_step)
        self.add_step(self.ingress_list_step)
        self.add_step(self.pvc_list_step)

    @property
    def description(self) -> str:
        """Step description."""
        return "Check status of all k8s resources in the selected namespaces."

    @property
    def component(self) -> str:
        """Component name."""
        return "ALL"

    @BaseStep.store_state
    def execute(self):
        """Check status of all k8s resources in the selected namespaces.

        Use settings values:
         - K8S_ONAP_NAMESPACE
         - STATUS_RESULTS_DIRECTORY
         - STORE_ARTIFACTS
         - CHECK_POD_VERSIONS
         - EXTRA_NAMESPACE_LIST
         - IGNORE_EMPTY_REPLICAS
         - INCLUDE_ALL_RES_IN_DETAILS
        """
        super().execute()

        self.pods = self.pod_list_step.all_resources
        self.services = self.service_list_step.all_resources
        self.jobs = self.job_list_step.all_resources
        self.deployments = self.deployment_list_step.all_resources
        self.replicasets = self.replicaset_list_step.all_resources
        self.statefulsets = self.statefulset_list_step.all_resources
        self.daemonsets = self.daemonset_list_step.all_resources
        self.pvcs = self.pvc_list_step.all_resources
        self.configmaps = self.configmap_list_step.all_resources
        self.secrets = self.secret_list_step.all_resources
        self.ingresses = self.ingress_list_step.all_resources

        self.failing_statefulsets = self.statefulset_list_step.failing_resources
        self.failing_jobs = self.job_list_step.failing_resources
        self.failing_deployments = self.deployment_list_step.failing_resources
        self.failing_replicasets = self.replicaset_list_step.failing_resources
        self.failing_daemonsets = self.daemonset_list_step.failing_resources
        self.failing_pvcs = self.pvc_list_step.failing_resources

        self.jinja_env.get_template('index.html.j2').stream(
            ns=self,
            delta=delta).dump('{}/index.html'.format(self.res_dir))
        self.jinja_env.get_template('raw_output.txt.j2').stream(
            ns=self, namespace=self.namespace).dump('{}/onap-k8s.log'.format(
                self.res_dir))

        details = {"namespace": {
            "all": settings.EXTRA_NAMESPACE_LIST,
            "resources": {}
        }}

        def store_results(result_dict, step):
            result_dict[step.resource_type] = {
                'number_failing': len(step.failing_resources),
                'failing': self.map_by_name(step.failing_resources)
            }
            if settings.INCLUDE_ALL_RES_IN_DETAILS:
                result_dict[step.resource_type]['all'] = self.map_by_name(step.all_resources)
                result_dict[step.resource_type]['number_all'] = len(step.all_resources)

        for step in self._steps:
            if step.failing:
                self.failing = True
                self.__logger.info("%s failing: %s",
                                   step.resource_type,
                                   len(step.failing_resources))
            if step.is_primary:
                store_results(details, step)
            else:
                ns_details = details["namespace"]["resources"]
                if step.namespace not in ns_details:
                    ns_details[step.namespace] = {}
                ns_details = ns_details[step.namespace]
                store_results(ns_details, step)

        with (Path(self.res_dir).joinpath(settings.STATUS_DETAILS_JSON)).open('w') as file:
            json.dump(details, file, indent=4)
        if self.failing:
            raise StatusCheckException

    def map_by_name(self, resources):
        return list(map(lambda resource: resource.name, resources))
