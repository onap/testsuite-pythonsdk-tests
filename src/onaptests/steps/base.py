from abc import ABC, abstractmethod
from typing import List


class BaseStep(ABC):
    """Base step class."""

    def __init__(self, cleanup: bool = False) -> None:
        """Step initialization.

        Args:
            cleanup(bool, optional): Determines if cleanup action should be called.

        """
        self._steps: List["BaseStep"] = []
        self._cleanup: bool = cleanup
        self._parent: "BaseStep" = None

    def add_step(self, step: "BaseStep") -> None:
        self._steps.append(step)
        step._parent: "BaseStep" = self

    @property
    def parent(self) -> "BaseStep":
        """Step parent.

        If parent is not set the step is a root one.
        """
        return self._parent

    @property
    def is_root(self) -> bool:
        """Is a root step.

        Step is a root if has no parent

        Returns:
            bool: True if step is a root step, False otherwise

        """
        return self._parent is None

    def execute(self) -> None:
        """Step's action.

        Run all substeps action before it's own action.
        Override this method and remember to call `super().action()` before.

        """
        for step in self._steps:
            step.execute()

    def cleanup(self) -> None:
        """Step's cleanup.

        Not all steps has to have cleanup method

        """
        if self._cleanup:
            for step in self._steps:
                step.cleanup()


class YamlTemplateBaseStep(BaseStep, ABC):

    @property
    @abstractmethod
    def yaml_template(self) -> dict:
        pass
