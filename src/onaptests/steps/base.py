import functools
import itertools
import logging
import logging.config
import os
import time
from abc import ABC, abstractmethod
from typing import Iterator, List, Optional

from onapsdk.aai.business import Customer
from onapsdk.configuration import settings
from onapsdk.exceptions import SDKException, SettingsError
from onaptests.steps.reports_collection import (Report, ReportsCollection,
                                                ReportStepStatus)
from onaptests.utils.exceptions import (OnapTestException,
                                        OnapTestExceptionGroup,
                                        SubstepExecutionException,
                                        SubstepExecutionExceptionGroup)


IF_VALIDATION = "PYTHON_SDK_TESTS_VALIDATION"


class SkipExecutionException(OnapTestException):
    """Ued only for validation purposes"""
    pass


class StoreStateHandler(ABC):

    @classmethod
    def store_state(cls, fun=None, *, cleanup=False):
        if fun is None:
            return functools.partial(cls.store_state, cleanup=cleanup)

        @functools.wraps(fun)
        def wrapper(self, *args, **kwargs):
            if (cleanup and self._state_clean) or (not cleanup and self._state_execute):
                raise RuntimeError(f"Sate of {self._step_title(cleanup)} already stored")
            if cleanup:
                self._state_clean = True
            else:
                self._state_execute = True
            initial_exception = None
            try:
                execution_status: Optional[ReportStepStatus] = ReportStepStatus.FAIL
                if cleanup:
                    self._start_cleanup_time = time.time()
                    try:
                        if self._executed and self._cleanup:
                            self._log_execution_state("START", cleanup)
                            if self._is_validation_only:
                                self._cleaned_up = True
                            else:
                                fun(self, *args, **kwargs)
                            execution_status = ReportStepStatus.PASS
                        else:
                            execution_status = ReportStepStatus.NOT_EXECUTED
                    except (OnapTestException, SDKException) as test_exc:
                        initial_exception = test_exc
                    finally:
                        self._log_execution_state(execution_status.name, cleanup)
                        self._cleanup_substeps()
                    if initial_exception:
                        new_exception = initial_exception
                        initial_exception = None
                        raise new_exception
                else:
                    if self.check_preconditions():
                        self._log_execution_state("START", cleanup)
                        fun(self, *args, **kwargs)
                        execution_status = ReportStepStatus.PASS
                    else:
                        execution_status = ReportStepStatus.NOT_EXECUTED
            except SkipExecutionException:
                execution_status = ReportStepStatus.PASS
            except SubstepExecutionException as substep_exc:
                if not cleanup:
                    execution_status = ReportStepStatus.NOT_EXECUTED
                if initial_exception:
                    substep_exc = OnapTestExceptionGroup("Cleanup Exceptions",
                                                         [initial_exception, substep_exc])
                raise substep_exc
            except (OnapTestException, SDKException) as test_exc:
                if initial_exception:
                    test_exc = OnapTestExceptionGroup("Cleanup Exceptions",
                                                      [initial_exception, test_exc])
                raise test_exc
            finally:
                if not cleanup:
                    self._log_execution_state(execution_status.name, cleanup)
                if cleanup:
                    self._cleanup_report = Report(
                        step_description=self._step_title(cleanup),
                        step_execution_status=execution_status,
                        step_execution_duration=time.time() - self._start_cleanup_time,
                        step_component=self.component
                    )
                else:
                    if not self._start_execution_time:
                        if execution_status != ReportStepStatus.NOT_EXECUTED:
                            self._logger.error("No execution start time saved for %s step. "
                                               "Fix it by call `super.execute()` "
                                               "in step class `execute()` method definition",
                                               self.name)
                        self._start_execution_time = time.time()
                    self._execution_report = Report(
                        step_description=self._step_title(cleanup),
                        step_execution_status=(execution_status if execution_status else
                                               ReportStepStatus.FAIL),
                        step_execution_duration=time.time() - self._start_execution_time,
                        step_component=self.component
                    )
        return wrapper


class BaseStep(StoreStateHandler, ABC):
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
        self._executed: bool = False
        self._cleaned_up: bool = False
        self._state_execute: bool = False
        self._state_clean: bool = False
        self._nesting_level = 0
        self._is_validation_only = os.environ.get(IF_VALIDATION) is not None

    def add_step(self, step: "BaseStep") -> None:
        """Add substep.

        Add substep and mark step as a substep parent.

        Args:
            step (BaseStep): Step object
        """
        self._steps.append(step)
        step._parent: "BaseStep" = self
        step._update_nesting_level()

    def _update_nesting_level(self) -> None:
        """Update step nesting level.

        Step nesting level allows to display relatino of steps during validation
        """
        self._nesting_level = 1 + self._parent._nesting_level
        for step in self._steps:
            step._update_nesting_level()

    @property
    def parent(self) -> "BaseStep":
        """Step parent.

        If parent is not set the step is a root one.
        """
        return self._parent

    @property
    def is_executed(self) -> bool:
        """Is step executed.

        Step is executed if execute() method was completed without errors

        Returns:
            bool: True if step is executed, False otherwise

        """
        return self._executed

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
        for step in reversed(self._steps):
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

    def _step_title(self, cleanup=False):
        cleanup_label = " Cleanup:" if cleanup else ":"
        return f"[{self.component}] {self.name}{cleanup_label} {self.description}"

    def _log_execution_state(self, state: str, cleanup=False):
        nesting_label = "" + "  " * self._nesting_level
        description = f"| {state} {self._step_title(cleanup)} |"
        self._logger.info(nesting_label + "*" * len(description))
        self._logger.info(nesting_label + description)
        self._logger.info(nesting_label + "*" * len(description))

    def check_preconditions(self) -> bool:
        """Check preconditions.

        Check if step preconditions are satisfied. If not, step is skipped
        without further consequences. If yes, execution is initiated

        Returns:
            bool: True if preconditions are satisfied, False otherwise

        """
        return True

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
        if self._steps:
            self._log_execution_state("CONTINUE")
        self._start_execution_time = time.time()
        self._executed = True
        if self._is_validation_only:
            raise SkipExecutionException()

    def _cleanup_substeps(self) -> None:
        """Substeps' cleanup.

        Substeps are cleaned-up in reversed order.
        We also try to cleanup steps if others failed

        """
        exceptions_to_raise = []
        for step in reversed(self._steps):
            try:
                if step._cleanup:
                    step.cleanup()
                else:
                    step._default_cleanup_handler()
            except (OnapTestException, SDKException) as substep_err:
                try:
                    raise SubstepExecutionException from substep_err
                except Exception as e:
                    exceptions_to_raise.append(e)
        if len(exceptions_to_raise) > 0:
            if len(exceptions_to_raise) == 1:
                raise exceptions_to_raise[0]
            else:
                raise SubstepExecutionExceptionGroup("Substep Exceptions", exceptions_to_raise)

    def cleanup(self) -> None:
        """Step's cleanup.

        Not all steps has to have cleanup method

        """
        # Step itself was cleaned-up, now time for children
        if not self._cleanup:
            # in this case we just make sure that store_state is run
            self._default_cleanup_handler()

    @StoreStateHandler.store_state(cleanup=True)
    def _default_cleanup_handler(self):
        self._cleaned_up = True

    @classmethod
    def set_proxy(cls, sock_http):
        """Set sock proxy."""
        onap_proxy = {}
        onap_proxy['http'] = sock_http
        onap_proxy['https'] = sock_http
        Customer.set_proxy(onap_proxy)

    def validate_execution(self):
        if self._is_validation_only:
            self._log_execution_state(f"VALIDATE [{self._executed}, {self._cleanup}]")
            if self._executed and self._cleanup and not self._cleaned_up:
                self._logger.error(f"{self._step_title()} Cleanup Not Executed")
                assert self._cleaned_up
            for step in reversed(self._steps):
                step.validate_execution()


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
