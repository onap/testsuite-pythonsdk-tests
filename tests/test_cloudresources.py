#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test onboard scenario."""
from unittest import mock

import pytest
from onaptests.actions.cloudresources import CloudResources
from onapsdk.aai.cloud_infrastructure import ( 
    CloudRegion,
    Complex
)
from onapsdk.aai.business import OwningEntity as AaiOwningEntity

from onapsdk.vid import OwningEntity

OWNING_ENTITY = {
    "errors": []
}
OWNING_ENTITIES_LIST = {
    "owning-entity": [
        {
            "owning-entity-id": "7cc45253-b7e5-4b94-8a09-3a0504d13b08",
            "owning-entity-name": "OE-ETE_Customer",
            "resource-version": "1587388597761"
        },
        {
            "owning-entity-id": "8e8d199b-3d45-4e6f-aa5d-d83d4b4e7c69",
            "owning-entity-name": "OE-Amine",
            "resource-version": "1591692159984"
        },
        {
            "owning-entity-id": "8e8d199b-3d45-4e6f-aa5d-d83d4b4e7c69",
            "owning-entity-name": "OE-Generic",
            "resource-version": "1591692159984",
        }
    ]
}

OWNING_ENTITIES_LIST2 = {
    "owning-entity": [
        {
            "owning-entity-id": "b3dcdbb0-edae-4384-b91e-2f114472520c",
            "owning-entity-name": "test",
            "resource-version": "1588145971158"
        }
    ]
}

@mock.patch.object(CloudRegion, 'get_by_id')
@mock.patch.object(Complex, 'create')
@mock.patch.object(CloudRegion, 'create')
@mock.patch.object(CloudRegion, 'link_to_complex')
@mock.patch.object(CloudRegion, 'add_esr_system_info')
@mock.patch.object(CloudRegion, 'add_tenant')
def test_declare_aai_region(mock_tenant, mock_esr, mock_link, mock_cloud, mock_complex, mock_get):
    service = CloudResources()
    mock_get.return_value = None
    service.declare_aai_region()
    mock_complex.assert_called_once()
    mock_cloud.assert_called_once()

@mock.patch.object(OwningEntity, "send_message_json")
@mock.patch.object(OwningEntity, "send_message")
@mock.patch.object(AaiOwningEntity, "send_message_json")
@mock.patch.object(AaiOwningEntity, "send_message")
def test_declare_owning_entity(mock_oe_create, mock_get, mock_create, mock_send):
    cloud = CloudResources()
    mock_send.return_value = OWNING_ENTITY
    mock_get.return_value = OWNING_ENTITIES_LIST
    oe = cloud.declare_owning_entity()
    assert oe.name == "OE-Generic"
    mock_send.return_value = OWNING_ENTITY
    mock_get.return_value = OWNING_ENTITIES_LIST2
    oe = cloud.declare_owning_entity()
    assert oe
