#!/usr/bin/env python

# Copyright (c) 2018 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
"""Module to define pythonsdk-test exceptions."""

__author__ = ("Morgan Richomme <morgan.richomme@orange.com>")


class TestConfigurationException(Exception):
    """Raise when configutation of the use cases is not complete or buggy."""


class ServiceDistributionException(Exception):
    """Service not properly distributed."""


class ServiceInstantiateException(Exception):
    """Service cannot be instantiate."""


class ServiceCleanupException(Exception):
    """Service cannot be cleaned."""


class VnfInstantiateException(Exception):
    """VNF cannot be instantiate."""


class VnfCleanupException(Exception):
    """VNF cannot be cleaned."""


class VfModuleInstantiateException(Exception):
    """VF Module cannot be instantiate."""


class VfModuleCleanupException(Exception):
    """VF Module cannot be instantiate."""


class NetworkInstantiateException(Exception):
    """Network cannot be instantiate."""


class NetworkCleanupException(Exception):
    """Network cannot be cleaned."""

class ProfileInformationException(Exception):
    """Missing k8s profile information."""

class ProfileCleanupException(Exception):
    """K8s profile cannot be cleaned."""
