# Copyright (c) 2018-2020 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
"""Module to define pythonsdk-test exceptions."""

__author__ = "Morgan Richomme <morgan.richomme@orange.com>"


class OnapTestException(Exception):
    """Parent Class for all Onap Test Exceptions."""
    def __init__(self, __message='Generic OnapTest exception', *args, **kwargs): # noqa: W1113
        super().__init__(__message, *args, **kwargs)
        self.error_message = __message
        if self.error_message:
            self.error_message = str(self.error_message)

    def __str__(self):
        values = self.root_cause
        if len(values) == 0:
            return ""
        if len(values) == 1:
            return str(values[0])
        return str(values)

    @property
    def root_cause(self):
        """Real reason of the test exception"""
        return [self.error_message]


class OnapTestExceptionGroup(OnapTestException, ExceptionGroup):  # noqa
    """Group of Onap Test Exceptions."""
    def __init__(self, __message='Generic OnapTest exception group', __exceptions=None):
        super().__init__(__message, __exceptions)


class TestConfigurationException(OnapTestException):
    """Raise when configuration of the use case is incomplete or buggy."""
    def __init__(self, __message='Configuration error'):
        super().__init__(__message)


class ServiceDistributionException(OnapTestException):
    """Service not properly distributed."""
    def __init__(self, __message='Service not well distributed'):
        super().__init__(__message)


class ServiceInstantiateException(OnapTestException):
    """Service cannot be instantiated."""
    def __init__(self, __message='Service instantiation error'):
        super().__init__(__message)


class ServiceCleanupException(OnapTestException):
    """Service cannot be cleaned."""
    def __init__(self, __message='Service not well cleaned up'):
        super().__init__(__message)


class VnfInstantiateException(OnapTestException):
    """VNF cannot be instantiated."""
    def __init__(self, __message='VNF instantiation error'):
        super().__init__(__message)


class VnfCleanupException(OnapTestException):
    """VNF cannot be cleaned."""
    def __init__(self, __message="VNF can't be cleaned"):
        super().__init__(__message)


class VfModuleInstantiateException(OnapTestException):
    """VF Module cannot be instantiated."""
    def __init__(self, __message='VF Module instantiation error'):
        super().__init__(__message)


class VfModuleCleanupException(OnapTestException):
    """VF Module cannot be cleaned."""
    def __init__(self, __message="VF Module can't be cleaned"):
        super().__init__(__message)


class NetworkInstantiateException(OnapTestException):
    """Network cannot be instantiated."""
    def __init__(self, __message='Network instantiation error'):
        super().__init__(__message)


class NetworkCleanupException(OnapTestException):
    """Network cannot be cleaned."""
    def __init__(self, __message="Network can't be cleaned"):
        super().__init__(__message)


class ProfileInformationException(OnapTestException):
    """Missing k8s profile information."""
    def __init__(self, __message='Missing k8s profile information'):
        super().__init__(__message)


class ProfileCleanupException(OnapTestException):
    """K8s profile cannot be cleaned."""
    def __init__(self, __message="Profile can't be cleaned"):
        super().__init__(__message)


class EnvironmentPreparationException(OnapTestException):
    """Test environment preparation exception."""
    def __init__(self, __message="Test can't be run properly due to preparation error"):
        super().__init__(__message)


class SubstepExecutionException(OnapTestException):
    """Exception raised if substep execution fails."""
    def __init__(self, __message, __exception):
        super().__init__(__message)
        self.sub_exception = __exception

    @property
    def root_cause(self):
        """Real reason of the test exception"""
        if hasattr(self, "sub_exception"):
            if isinstance(self.sub_exception, OnapTestException):
                return self.sub_exception.root_cause
            return [str(self.sub_exception)]
        return super().root_cause


class SubstepExecutionExceptionGroup(ExceptionGroup, SubstepExecutionException):  # noqa
    """Group of Substep Exceptions."""
    def __init__(self, __message="Substeps group has failed",
                 __exceptions=None):
        super().__init__(__message, __exceptions)
        self.sub_exceptions = __exceptions

    @property
    def root_cause(self):
        """Real reason of the test exception"""
        if self.sub_exceptions:
            values = []
            for exc in self.sub_exceptions:
                if isinstance(exc, OnapTestException):
                    values.extend(exc.root_cause)
                else:
                    values.append(str(exc))
            return values
        return super().root_cause


class EnvironmentCleanupException(OnapTestException):
    """Test environment cleanup exception."""
    def __init__(self, __message="Test couldn't finish a cleanup"):
        super().__init__(__message)


class PolicyException(OnapTestException):
    """Policy exception."""
    def __init__(self, __message="Problem with policy module"):
        super().__init__(__message)


class DcaeException(OnapTestException):
    """DCAE exception."""
    def __init__(self, __message="Problem with DCAE module"):
        super().__init__(__message)


class StatusCheckException(OnapTestException):
    """Status Check exception."""
    def __init__(self, __message="Namespace status check has failed"):
        super().__init__(__message)
