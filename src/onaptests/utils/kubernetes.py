import base64

from kubernetes import client, config
from onapsdk.configuration import settings

from onaptests.utils.exceptions import EnvironmentPreparationException


class KubernetesHelper:
    """Helper class to perform operations on kubernetes cluster"""

    @classmethod
    def load_config(cls):
        """Load kubernetes client configuration"""
        if settings.IN_CLUSTER:
            config.load_incluster_config()
        else:
            config.load_kube_config(config_file=settings.K8S_CONFIG)

    @classmethod
    def get_credentials_from_secret(cls,
                                    secret_name: str,
                                    login_key: str,
                                    password_key: str,
                                    namespace: str = settings.K8S_ONAP_NAMESPACE):
        """Resolve SDNC datbase credentials from k8s secret.

        Args:
            secret_name (str): name of the secret to load
            login_key (str): key of the login in secret
            password_key (str): key of the password in secret
            namespace (str): k8s namespace to load key from
        """

        cls.load_config()
        api_instance = client.CoreV1Api()
        try:
            secret = api_instance.read_namespaced_secret(secret_name, namespace)
            if secret.data:
                if (login_key in secret.data and password_key in secret.data):
                    login_base64 = secret.data[login_key]
                    login = base64.b64decode(login_base64).decode("utf-8")
                    password_base64 = secret.data[password_key]
                    password = base64.b64decode(password_base64).decode("utf-8")
                    return login, password
                raise EnvironmentPreparationException(
                    "Login key or password key not found in secret")
            raise EnvironmentPreparationException("Secret data not found in secret")
        except client.rest.ApiException as e:
            raise EnvironmentPreparationException("Error accessing secret") from e
