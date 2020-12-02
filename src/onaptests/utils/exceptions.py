# Copyright (c) 2018-2020 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
"""Module to define pythonsdk-test exceptions."""

__author__ = ("Morgan Richomme <morgan.richomme@orange.com>")

class  OnapTestException(Exception):
    """Parent Class for all Onap Test Exceptions."""
    error_message='Generic OnapTest exception'

class TestConfigurationException(OnapTestException):
    """Raise when configuration of the use case is incomplete or buggy."""
    error_message='Configuration error'

class ServiceDistributionException(OnapTestException):
    """Service not properly distributed."""
    error_message='Service not well distributed'


class ServiceInstantiateException(OnapTestException):
    """Service cannot be instantiated."""
    error_message='Service instantiation error'


class ServiceCleanupException(OnapTestException):
    """Service cannot be cleaned."""
    error_message='Service not well cleaned up'


class VnfInstantiateException(OnapTestException):
    """VNF cannot be instantiated."""
    error_message='VNF instantiation error'


class VnfCleanupException(OnapTestException):
    """VNF cannot be cleaned."""
    error_message="VNF can't be cleaned"


class VfModuleInstantiateException(OnapTestException):
    """VF Module cannot be instantiated."""
    error_message='VF Module instantiation error'


class VfModuleCleanupException(OnapTestException):
    """VF Module cannot be cleaned."""
    error_message="VF Module can't be cleaned"


class NetworkInstantiateException(OnapTestException):
    """Network cannot be instantiated."""
    error_message='Network instantiation error'


class NetworkCleanupException(OnapTestException):
    """Network cannot be cleaned."""
    error_message="Network can't be cleaned"

class ProfileInformationException(OnapTestException):
    """Missing k8s profile information."""
    error_message='Missing k8s profile information'

class ProfileCleanupException(OnapTestException):
    """K8s profile cannot be cleaned."""
    error_message="Profile can't be cleaned"
