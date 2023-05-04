"""Resources module."""


class K8sResource():
    """K8sResource class."""

    def __init__(self, k8s=None):
        """Init the k8s resource."""
        self.k8s = k8s
        self.name = ""
        self.events = []
        if self.k8s:
            self.name = self.k8s.metadata.name
            self.specific_k8s_init()

    def specific_k8s_init(self):
        """Do the specific part for k8s resource when k8s object is present."""
        pass

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if (isinstance(other, K8sResource)):
            return self.name == other.name
        else:
            return False

class K8sPodParentResource(K8sResource):
    """K8sPodParentResource class."""

    def __init__(self, k8s=None):
        """Init the k8s pod parent resource."""
        self.pods = []
        self.failed_pods = 0
        super().__init__(k8s=k8s)


class Pod(K8sResource):
    """Pod class."""

    def __init__(self, k8s=None):
        """Init the pod."""
        self.containers = []
        self.init_containers = []
        self.running_containers = 0
        self.runned_init_containers = 0
        self.volumes = {}
        self.restart_count = 0
        self.init_restart_count = 0
        self.init_done = True
        super().__init__(k8s=k8s)

    def specific_k8s_init(self):
        """Specific k8s init."""
        self.set_volumes(self.k8s.spec.volumes)

    def set_volumes(self, volumes):
        """Generate the volume list."""
        for volume in volumes:
            volume_name = volume.name
            self.volumes[volume_name] = {}
            for volume_type in volume.attribute_map:
                if volume_type != "name" and getattr(volume, volume_type):
                    self._parse_volume_type(volume, volume_name, volume_type)

    def _parse_volume_type(self, volume, name, volume_type):
        """Parse volume type informations."""
        self.volumes[name][volume_type] = {}
        infos = getattr(volume, volume_type)
        for details in infos.attribute_map:
            self.volumes[name][volume_type][details] = getattr(infos, details)

    def ready(self):
        """Calculate if Pod is ready."""
        if self.init_done and self.running_containers == len(self.containers):
            return True
        return False


class Container():
    """Container class."""

    def __init__(self, name=""):
        """Init the container."""
        self.name = name
        self.status = ""
        self.ready = False
        self.restart_count = 0
        self.image = ""

    def set_status(self, status):
        """Generate status for container."""
        if status.running:
            self.status = "Running"
        else:
            if status.terminated:
                self.status = "Terminated ({})".format(
                    status.terminated.reason)
            else:
                if status.waiting:
                    self.status = "Waiting ({})".format(
                        status.waiting.reason)
                else:
                    self.status = "Unknown"


class Service(K8sPodParentResource):
    """Service class."""

    def __init__(self, k8s=None):
        """Init the service."""
        self.type = ""
        super().__init__(k8s=k8s)

    def specific_k8s_init(self):
        """Do the specific part for service when k8s object is present."""
        self.type = self.k8s.spec.type


class Job(K8sPodParentResource):
    """Job class."""


class Deployment(K8sPodParentResource):
    """Deployment class."""

class ReplicaSet(K8sPodParentResource):
    """ReplicaSet class."""

class StatefulSet(K8sPodParentResource):
    """StatefulSet class."""


class DaemonSet(K8sPodParentResource):
    """DaemonSet class."""


class Pvc(K8sResource):
    """Pvc class."""


class ConfigMap(K8sResource):
    """ConfigMap class."""


class Secret(K8sResource):
    """Secret class."""


class Ingress(K8sResource):
    """Ingress class."""