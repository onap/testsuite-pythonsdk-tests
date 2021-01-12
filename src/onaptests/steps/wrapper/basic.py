"""Basic container commands to Docker."""
import docker
from onaptests.steps.base import BaseStep
from onaptests.utils.simulators import get_config


class SimulatorBasic(BaseStep):
    """Basic operations on a docker container."""

    def __init__(self, cleanup=False, config_filename=None):
        """Initialize config path and docker client."""
        super().__init__(cleanup=cleanup)
        self.client = docker.from_env()
        self.config = get_config(config_filename)

    @property
    def description(self) -> str:
        """Step description."""
        return "Run a simulator container."

    @property
    def component(self) -> str:
        """Component name."""
        return "Environment"

    @BaseStep.store_state
    def execute(self) -> None:
        """Run a simulator container.

        1. Pull an image from a registry
        2. Run a container
        """
        image = self.config["image"]
        name = self.config["container_name"]

        container = self.client.containers.run(image=image, name=name, detach=True)
        container.start()


    def cleanup(self) -> None:
        """Remove the simulator container.

        1. Stop the container
        2. Remove the container
        3. Remove the image
        """
        name = self.config["container_name"]

        container = self.client.containers.get(container_id=name)
        image = container.image
        container.stop()
        container.remove()
        self.client.images.remove(image.id)
