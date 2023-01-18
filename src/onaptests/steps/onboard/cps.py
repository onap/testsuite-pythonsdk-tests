# http://www.apache.org/licenses/LICENSE-2.0
"""CPS onboard module."""
from abc import ABC

from onapsdk.configuration import settings
from onapsdk.cps import Anchor, Dataspace, SchemaSet

from ..base import BaseStep


class CpsBaseStep(BaseStep, ABC):
    """Abstract CPS base step."""

    @property
    def component(self) -> str:
        """Component name."""
        return "CPS"


class CreateCpsDataspaceStep(CpsBaseStep):
    """Step to create a dataspace."""

    @property
    def description(self) -> str:
        """Step description."""
        return "Create CPS dataspace."

    @BaseStep.store_state
    def execute(self) -> None:
        """Create a dataspace."""
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

    def __init__(self, cleanup: bool = False) -> None:
        """Initialize step.

        Substeps:
            - CreateCpsDataspaceStep.
        """
        super().__init__(cleanup)
        self.add_step(CreateCpsDataspaceStep(cleanup))

    @property
    def description(self) -> str:
        """Step description."""
        return "Create CPS bookstore schema set"

    @BaseStep.store_state
    def execute(self) -> None:
        """Get dataspace created on substep and create schema-set."""
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

    def __init__(self, cleanup: bool = False) -> None:
        """Initialize step.

        Substeps:
            - CreateCpsSchemaSetStep.
        """
        super().__init__(cleanup)
        self.add_step(CreateCpsSchemaSetStep(cleanup))

    @property
    def description(self) -> str:
        """Step description."""
        return "Create CPS anchor"

    @BaseStep.store_state
    def execute(self) -> None:
        """Create anchor.

        Get dataspace and schema-set created substeps and create anchor.
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
    """Step to check node on anchor creation."""

    def __init__(self, cleanup: bool = False) -> None:
        """Initialize step.

        Substeps:
            - CreateCpsAnchorStep.
        """
        super().__init__(cleanup)
        self.add_step(CreateCpsAnchorStep(cleanup))

    @property
    def description(self) -> str:
        """Step description."""
        return "Create CPS anchor node"

    @BaseStep.store_state
    def execute(self) -> None:
        """Create a node on an anchor created on substep."""
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
