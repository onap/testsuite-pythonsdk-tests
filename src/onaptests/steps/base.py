import logging
import logging.config
import time

from abc import ABC, abstractmethod
<<<<<<< HEAD   (ffb384 [RELEASE] Fix pbr version to avoid docker build error)
from typing import List
=======
from typing import Iterator, List, Optional
from onapsdk.aai.business import Customer
>>>>>>> CHANGE (0a315a Basic VM macro)
from onapsdk.configuration import settings
from onapsdk.aai.business import Customer

from .reports_collection import Report, ReportsCollection, ReportStepStatus


class BaseStep(ABC):
    """Base step class."""

    _logger: logging.Logger = logging.getLogger("")

    def __init_subclass__(cls):
        """Subclass initialization.

        Add _logger property for any BaseStep subclass
        """
        super().__init_subclass__()
        cls._logger: logging.Logger = logging.getLogger("")
        logging.config.dictConfig(settings.LOG_CONFIG)
        # Setup Proxy if SOCK_HTTP is defined in settings
        try:
            cls.set_proxy(settings.SOCK_HTTP)
        except AttributeError:
            pass

    def __init__(self, cleanup: bool = False) -> None:
        """Step initialization.

        Args:
            cleanup(bool, optional): Determines if cleanup action should be called.

        """
        self._steps: List["BaseStep"] = []
        self._cleanup: bool = cleanup
        self._parent: "BaseStep" = None
        self._reports_collection: ReportsCollection = None

    def add_step(self, step: "BaseStep") -> None:
        """Add substep.

        Add substep and mark step as a substep parent.

        Args:
            step (BaseStep): Step object
        """
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

    @property
    def reports_collection(self) -> ReportsCollection:
        """Collection to store step reports.

        Store there if step result is "PASS" or "FAIL"

        Returns:
            Queue: Thread safe collection to store reports

        """
        if not self.is_root:
            return self.parent.reports_collection
        if not self._reports_collection:
            self._reports_collection = ReportsCollection()
        return self._reports_collection

    @property
    def name(self) -> str:
        """Step name."""
        return self.__class__.__name__

    @property
    @abstractmethod
    def description(self) -> str:
        """Step description.

        Used for reports

        Returns:
            str: Step description

        """

    @property
    @abstractmethod
    def component(self) -> str:
        """Component name.

        Name of component which step is related with.
            Most is the name of ONAP component.

        Returns:
            str: Component name

        """

    @classmethod
    def store_state(cls, fun):
        def wrapper(self, *args, **kwargs):
            try:
<<<<<<< HEAD   (ffb384 [RELEASE] Fix pbr version to avoid docker build error)
                start_time: float = time.time()
=======
                if cleanup:
                    self._start_cleanup_time = time.time()
                execution_status: Optional[ReportStepStatus] = None
>>>>>>> CHANGE (0a315a Basic VM macro)
                ret = fun(self, *args, **kwargs)
                execution_status = ReportStepStatus.PASS
                return ret
<<<<<<< HEAD   (ffb384 [RELEASE] Fix pbr version to avoid docker build error)
            except Exception:
                execution_status: ReportStepStatus = ReportStepStatus.FAIL
=======
            except SubstepExecutionException:
                execution_status = ReportStepStatus.PASS if cleanup else ReportStepStatus.NOT_EXECUTED
                raise
            except (OnapTestException, SDKException):
                execution_status = ReportStepStatus.FAIL
>>>>>>> CHANGE (0a315a Basic VM macro)
                raise
            finally:
                self.reports_collection.put(
                    Report(
                        step_description=f"[{self.component}] {self.name}: {self.description}",
<<<<<<< HEAD   (ffb384 [RELEASE] Fix pbr version to avoid docker build error)
                        step_execution_status=execution_status,
                        step_execution_duration=time.time() - start_time
=======
                        step_execution_status=execution_status if execution_status else ReportStepStatus.FAIL,
                        step_execution_duration=time.time() - self._start_execution_time
>>>>>>> CHANGE (0a315a Basic VM macro)
                    )
                )
        return wrapper

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

    @classmethod
    def set_proxy(cls, sock_http):
        """Set sock proxy."""
        onap_proxy = {}
        onap_proxy['http'] = sock_http
        onap_proxy['https'] = sock_http
        Customer.set_proxy(onap_proxy)


class YamlTemplateBaseStep(BaseStep, ABC):
    """Base YAML template step."""

    @property
    @abstractmethod
    def yaml_template(self) -> dict:
        """YAML template abstract property.

        Every YAML template step need to implement that property.

        Returns:
            dict: YAML template

        """
