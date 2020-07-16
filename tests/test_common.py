#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test onboard scenario."""

import pytest
from onaptests.actions.common import Common



def test_get_service_custom_config():
    """Check get_service_custom_config with only service arg."""
    common_instance = Common()
    service_params = common_instance.get_service_custom_config("ubuntu16")
    assert service_params['version'] == "1.0"

def test_get_service_custom_config_with_arg1():
    """Check get_service_custom_config with both args."""
    
    common_instance = Common()
    service_params = common_instance.get_service_custom_config("ubuntu16", "version")
    assert service_params == "1.0"

def test_get_service_custom_config_error1():
    """Check get_service_custom_config with undefined parameter"""
    common_instance = Common()
    with pytest.raises(ValueError):
        service_params = common_instance.get_service_custom_config("ubuntu16", "toto")

def test_get_service_custom_config_error2():
    """Check get_service_custom_config with undefined file"""
    common_instance = Common()
    with pytest.raises(ValueError):
        service_params = common_instance.get_service_custom_config("notexist", "version")
