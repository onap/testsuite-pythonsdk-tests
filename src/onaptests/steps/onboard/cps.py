# http://www.apache.org/licenses/LICENSE-2.0
"""CPS onboard module."""
import base64
from abc import ABC

import pg8000
from kubernetes import client, config
from onapsdk.configuration import settings
from onapsdk.cps import Anchor, Dataspace, SchemaSet

from onaptests.utils.exceptions import EnvironmentPreparationException

from ..base import BaseStep


class CpsBaseStep(BaseStep, ABC):
    """Abstract CPS base step."""

    @property
    def component(self) -> str:
        """Component name."""
        return "CPS"


class CreateCpsDataspaceStep(CpsBaseStep):
    """Step to create a dataspace."""

    def __init__(self) -> None:
        """Initialize step."""
        super().__init__(cleanup=settings.CLEANUP_FLAG)

    @property
    def description(self) -> str:
        """Step description."""
        return "Create CPS dataspace."

    @BaseStep.store_state
    def execute(self) -> None:
        """Create a dataspace.

        Use settings values:
         - DATASPACE_NAME.

        """
        super().execute()
        Dataspace.create(settings.DATASPACE_NAME)

    @BaseStep.store_state(cleanup=True)
    def cleanup(self) -> None:
        """Delete created dataspace."""
        dataspace: Dataspace = Dataspace(settings.DATASPACE_NAME)
        dataspace.delete()
        super().cleanup()


class CreateCpsSchemaSetStep(CpsBaseStep):
    """Step to check schema-set creation."""

    def __init__(self) -> None:
        """Initialize step.

        Substeps:
            - CreateCpsDataspaceStep.
        """
        super().__init__(cleanup=settings.CLEANUP_FLAG)
        self.add_step(CreateCpsDataspaceStep())

    @property
    def description(self) -> str:
        """Step description."""
        return "Create CPS bookstore schema set"

    @BaseStep.store_state
    def execute(self) -> None:
        """Get dataspace created on substep and create schema-set.

        Use settings values:
         - DATASPACE_NAME,
         - SCHEMA_SET_NAME.

        """
        super().execute()
        dataspace: Dataspace = Dataspace(settings.DATASPACE_NAME)
        with settings.SCHEMA_SET_FILE.open("rb") as schema_set_file:
            dataspace.create_schema_set(settings.SCHEMA_SET_NAME, schema_set_file)

    @BaseStep.store_state(cleanup=True)
    def cleanup(self) -> None:
        """Delete created schema-set."""
        dataspace: Dataspace = Dataspace(settings.DATASPACE_NAME)
        schema_set = dataspace.get_schema_set(settings.SCHEMA_SET_NAME)
        schema_set.delete()
        super().cleanup()


class CreateCpsAnchorStep(CpsBaseStep):
    """Step to create an anchor."""

    def __init__(self) -> None:
        """Initialize step.

        Substeps:
            - CreateCpsSchemaSetStep.
        """
        super().__init__(cleanup=settings.CLEANUP_FLAG)
        self.add_step(CreateCpsSchemaSetStep())

    @property
    def description(self) -> str:
        """Step description."""
        return "Create CPS anchor"

    @BaseStep.store_state
    def execute(self) -> None:
        """Create anchor.

        Get dataspace and schema-set created substeps and create anchor.

        Use settings values:
         - DATASPACE_NAME,
         - SCHEMA_SET_NAME,
         - ANCHOR_DATA.

        """
        super().execute()
        dataspace: Dataspace = Dataspace(settings.DATASPACE_NAME)
        schema_set: SchemaSet = dataspace.get_schema_set(settings.SCHEMA_SET_NAME)
        dataspace.create_anchor(schema_set, settings.ANCHOR_NAME)

    @BaseStep.store_state(cleanup=True)
    def cleanup(self) -> None:
        """Delete an anchor."""
        dataspace: Dataspace = Dataspace(settings.DATASPACE_NAME)
        anchor: Anchor = dataspace.get_anchor(settings.ANCHOR_NAME)
        anchor.delete()
        super().cleanup()


class CreateCpsAnchorNodeStep(CpsBaseStep):
    """Step to create anchor node."""

    def __init__(self) -> None:
        """Initialize step.

        Substeps:
            - CreateCpsAnchorStep.
        """
        super().__init__(cleanup=settings.CLEANUP_FLAG)
        self.add_step(CreateCpsAnchorStep())

    @property
    def description(self) -> str:
        """Step description."""
        return "Create CPS anchor node"

    @BaseStep.store_state
    def execute(self) -> None:
        """Create a node on an anchor created on substep.

        Use settings values:
         - DATASPACE_NAME,
         - ANCHOR_NAME,
         - ANCHOR_DATA.

         """
        super().execute()
        dataspace: Dataspace = Dataspace(settings.DATASPACE_NAME)
        anchor: Anchor = dataspace.get_anchor(settings.ANCHOR_NAME)
        anchor.create_node(settings.ANCHOR_DATA)

    @BaseStep.store_state(cleanup=True)
    def cleanup(self) -> None:
        """Delete nodes."""
        dataspace: Dataspace = Dataspace(settings.DATASPACE_NAME)
        anchor: Anchor = dataspace.get_anchor(settings.ANCHOR_NAME)
        anchor.delete_nodes("/")
        super().cleanup()


class UpdateCpsAnchorNodeStep(CpsBaseStep):
    """Step to update node on anchor creation."""

    def __init__(self) -> None:
        """Initialize step.

        Substeps:
            - CreateCpsAnchorNodeStep.
        """
        super().__init__(cleanup=BaseStep.HAS_NO_CLEANUP)
        self.add_step(CreateCpsAnchorNodeStep())

    @property
    def description(self) -> str:
        """Step description."""
        return "Update CPS anchor node"

    @BaseStep.store_state
    def execute(self) -> None:
        """Update a node on an anchor created on substep.

        Use settings values:
         - DATASPACE_NAME,
         - ANCHOR_NAME,
         - ANCHOR_DATA_2.

         """
        super().execute()
        dataspace: Dataspace = Dataspace(settings.DATASPACE_NAME)
        anchor: Anchor = dataspace.get_anchor(settings.ANCHOR_NAME)
        anchor.update_node("/", settings.ANCHOR_DATA_2)


class QueryCpsAnchorNodeStep(CpsBaseStep):
    """Step to check query on node."""

    def __init__(self) -> None:
        """Initialize step.

        Substeps:
            - UpdateCpsAnchorNodeStep.

        """
        super().__init__(cleanup=BaseStep.HAS_NO_CLEANUP)
        self.add_step(UpdateCpsAnchorNodeStep())

    @property
    def description(self) -> str:
        """Step description."""
        return "Query node"

    @BaseStep.store_state
    def execute(self) -> None:
        """Query on node on an anchor created on substep.

        Use settings values:
         - DATASPACE_NAME,
         - ANCHOR_NAME,
         - QUERY_1,
         - QUERY_2,
         - QUERY_3.

         """
        super().execute()
        dataspace: Dataspace = Dataspace(settings.DATASPACE_NAME)
        anchor: Anchor = dataspace.get_anchor(settings.ANCHOR_NAME)
        anchor.query_node(settings.QUERY_1)
        anchor.query_node(settings.QUERY_2)
        anchor.query_node(settings.QUERY_3)


class CheckPostgressDataBaseConnectionStep(CpsBaseStep):
    """Step to test connection with postgress."""

    def __init__(self) -> None:
        """Initialize step."""
        super().__init__(cleanup=BaseStep.HAS_NO_CLEANUP)

    @property
    def description(self) -> str:
        """Step description."""
        return "Establish connection with Postgress and execute the query"

    def get_database_credentials(self):
        config.load_kube_config()
        api_instance = client.CoreV1Api()
        try:
            secret = api_instance.read_namespaced_secret(
                settings.SECRET_NAME, settings.K8S_ONAP_NAMESPACE)
            if secret.data:
                if settings.DB_LOGIN in secret.data and settings.DB_PASSWORD in secret.data:
                    login_base64 = secret.data[settings.DB_LOGIN]
                    self.login = base64.b64decode(login_base64).decode("utf-8")
                    password_base64 = secret.data[settings.DB_PASSWORD]
                    self.password = base64.b64decode(password_base64).decode("utf-8")
                else:
                    raise EnvironmentPreparationException(
                        "Login key or password key not found in secret")
            else:
                raise EnvironmentPreparationException("Secret data not found in secret")
        except client.rest.ApiException as e:
            self.login = None
            self.password = None
            raise EnvironmentPreparationException("Error accessing secret") from e

    def connect_to_postgress(self):
        self.get_database_credentials()
        if self.login and self.password:
            db_params = {
                "user": self.login,
                "password": self.password,
                "host": settings.DB_PRIMARY_HOST,
                "database": settings.DATABASE,
                "port": settings.DB_PORT
            }
            try:
                connection = pg8000.connect(**db_params)
                cursor = connection.cursor()
                select_query = "SELECT * FROM yang_resource LIMIT 1;"
                cursor.execute(select_query)
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()
            except pg8000.Error as e:
                self._logger.exception(f"Error while connecting to PostgreSQL: {str(e)}")
                raise

    @BaseStep.store_state
    def execute(self) -> None:
        """Establish connection with Postgress and execute the query.

        Use settings values:
         - DB_PRIMARY_HOST,
         - DATABASE,
         - DB_PORT,
         - K8S_ONAP_NAMESPACE,
         - SECRET_NAME,
         - DB_LOGIN,
         - DB_PASSWORD.

         """
        super().execute()
        self.connect_to_postgress()
