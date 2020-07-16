from abc import ABC, abstractmethod
from typing import List


class BaseComponent(ABC):
    """Base component class."""

    def __init__(self, cleanup: bool = False) -> None:
        """Component initialization.
        
        Args:
            cleanup(bool, optional): Determines if cleanup action should be called.
        
        """
        self._subcomponents: List["BaseComponent"] = []
        self._cleanup: bool = cleanup

    def add_subcomponent(self, subcomponent: "BaseComponent") -> None:
        self._subcomponents.append(subcomponent)

    def action(self) -> None:
        """Component's action.
        
        Run all subcomponents action before it's own action.
        Override this method and remember to call `super().action()` before.

        """
        for subcomponent in self._subcomponents:
            subcomponent.action()

    def cleanup(self) -> None:
        """Component's cleanup.

        Not all components has to have cleanup method

        """
        pass
