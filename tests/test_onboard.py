#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test onboard scenario."""
from unittest import mock

import pytest
from onaptests.actions.onboard import Onboard

from onapsdk.sdc.service import Service
from onapsdk.sdc.vf import Vf
from onapsdk.sdc.vsp import Vsp
from onapsdk.sdc.vendor import Vendor

def test_init_with_args():
    """Check init with args."""
    onboard = Onboard(service_name= "test")
    # assert isinstance(vendor, SdcElement)
    assert onboard.service_name == "test"
    assert onboard.vsp_name == "testVSP"
    assert onboard.vf_name == "test_VF"

def test_init_without_args1():
    """Check init without arg service_name"""
    with pytest.raises(ValueError):
        onboard = Onboard()

@mock.patch.object(Service, 'onboard')
@mock.patch.object(Vf, 'onboard')
@mock.patch.object(Vsp, 'onboard')
@mock.patch.object(Vendor, 'onboard')
def test_onboard_resources(mock_vendor, mock_vsp, mock_vf, mock_service):
    onboard = Onboard(service_name= "ubuntu16")
    onboard.onboard_resources()
    mock_vendor.assert_called_once()
    mock_vsp.assert_called_once()
    mock_vf.assert_called_once()
    mock_service.assert_called_once()
