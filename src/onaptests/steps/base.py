import functools
import itertools
import logging
import logging.config
import time

from abc import ABC, abstractmethod
from typing import Iterator, List, Optional
from onapsdk.aai.business import Customer
from onapsdk.configuration import settings
from onapsdk.exceptions import SDKException, SettingsError

from onaptests.steps.reports_collection import Report, ReportsCollection, ReportStepStatus
from onaptests.utils.exceptions import OnapTestException, SubstepExecutionException


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
        except SettingsError:
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
        self._start_execution_time: float = None
        self._start_cleanup_time: float = None
        self._execution_report: ReportStepStatus = None
        self._cleanup_report: ReportStepStatus = None

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
            for step_report in itertools.chain(self.execution_reports, self.cleanup_reports):
                self._reports_collection.put(step_report)
        return self._reports_collection

    @property
    def execution_reports(self) -> Iterator[ReportsCollection]:
        """Execution reports generator.

        Steps tree postorder traversal

        Yields:
            Iterator[ReportsCollection]: Step execution report

        """
        for step in self._steps:
            yield from step.execution_reports
        if self._execution_report:
            yield self._execution_report

    @property
    def cleanup_reports(self) -> Iterator[ReportsCollection]:
        """Cleanup reports generator.

        Steps tree preorder traversal

        Yields:
            Iterator[ReportsCollection]: Step cleanup report

        """
        if self._cleanup:
            if self._cleanup_report:
                yield self._cleanup_report
            for step in self._steps:
                yield from step.cleanup_reports

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
    def store_state(cls, fun=None, *, cleanup=False):
        if fun is None:
            return functools.partial(cls.store_state, cleanup=cleanup)
        @functools.wraps(fun)
        def wrapper(self, *args, **kwargs):
            try:
                if cleanup:
                    self._start_cleanup_time = time.time()
                execution_status: Optional[ReportStepStatus] = None
                ret = fun(self, *args, **kwargs)
                execution_status = ReportStepStatus.PASS
                return ret
            except SubstepExecutionException:
                execution_status = ReportStepStatus.PASS if cleanup else ReportStepStatus.NOT_EXECUTED
                raise
            except (OnapTestException, SDKException):
                execution_status = ReportStepStatus.FAIL
                raise
            finally:
                if cleanup:
                    self._cleanup_report = Report(
                        step_description=f"[{self.component}] {self.name} cleanup: {self.description}",
                        step_execution_status=execution_status,
                        step_execution_duration=time.time() - self._start_cleanup_time
                    )
                else:
                    if not self._start_execution_time:
                        if execution_status != ReportStepStatus.NOT_EXECUTED:
                            self._logger.error("No execution start time saved for %s step. Fix it by call `super.execute()` "
                                               "in step class `execute()` method definition", self.name)
                        self._start_execution_time = time.time()
                    self._execution_report = Report(
                        step_description=f"[{self.component}] {self.name}: {self.description}",
                        step_execution_status=execution_status if execution_status else ReportStepStatus.FAIL,
                        step_execution_duration=time.time() - self._start_execution_time
                    )
        return wrapper

    def execute(self) -> None:
        """Step's action execution.

        Run all substeps action before it's own action.
        Override this method and remember to call `super().execute()` before.

        """
        for step in self._steps:
            try:
                step.execute()
            except (OnapTestException, SDKException) as substep_err:
                raise SubstepExecutionException from substep_err
        self._start_execution_time = time.time()

    def cleanup(self) -> None:
        """Step's cleanup.

        Not all steps has to have cleanup method

        """
        if self._cleanup:
            for step in self._steps:
                try:
                    step.cleanup()
                except (OnapTestException, SDKException) as substep_err:
                    raise SubstepExecutionException from substep_err

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

    @property
    @abstractmethod
    def model_yaml_template(self) -> dict:
        """Model YAML template abstract property.

        Every YAML template step need to implement that property.

        Returns:
            dict: YAML template

        """
