#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test onboard scenario."""
from unittest import mock
from typing import Iterator

import pytest
from onaptests.actions.instantiate import Instantiate
import onapsdk.constants as const
from onapsdk.sdc import SDC
from onapsdk.aai.aai_element import AaiElement
from onapsdk.aai.cloud_infrastructure import ( 
    CloudRegion,
    Complex,
    Tenant
)
from onapsdk.aai.business import (
    ServiceInstance,
    VnfInstance,
    VfModuleInstance,
    Customer,
    ServiceSubscription,
    OwningEntity as AaiOwningEntity
)
from onapsdk.sdc.service import Service, Vnf
from onapsdk.onap_service import OnapService
from onapsdk.so.instantiation import (
    ServiceInstantiation,
    VnfInstantiation,
    VnfParameter
)
from onapsdk.so.so_element import OrchestrationRequest
from onapsdk.vid import LineOfBusiness, Platform, Project
SIMPLE_CUSTOMER = {
    "customer": [
        {
            "global-customer-id": "generic",
            "subscriber-name": "generic",
            "subscriber-type": "INFRA",
            "resource-version": "1561218640404",
        }
    ]
}
CUSTOMERS = {
    "customer": [
        {
            "subscriber-name": "generic",
            "subscriber-type": "INFRA",
            "global-customer-id": "generic",
            "resource-version": "1581510772967",
        }
    ]
}

CUSTOMER_TEST = {
    "subscriber_name": "generic",
    "subscriber_type": "INFRA",
    "global-customer-id": "generic",
    "resource-version": "1581510772967",
}

SUBSCRIPTION_TYPES_LIST = {
    "service-subscription": [
        {
            "service-type": "test2",
            "resource-version": "1562591478146",
            "relationship-list": {
                "relationship": [
                    {
                        "related-to": "tenant",
                        "relationship-label": "org.onap.relationships.inventory.Uses",
                        "related-link": "/aai/v16/cloud-infrastructure/cloud-regions/cloud-region/OPNFV/RegionOne/tenants/tenant/4bdc6f0f2539430f9428c852ba606808",
                        "relationship-data": [
                            {
                                "relationship-key": "cloud-region.cloud-owner",
                                "relationship-value": "OPNFV",
                            },
                            {
                                "relationship-key": "cloud-region.cloud-region-id",
                                "relationship-value": "RegionOne",
                            },
                            {
                                "relationship-key": "tenant.tenant-id",
                                "relationship-value": "4bdc6f0f2539430f9428c852ba606808",
                            },
                        ],
                        "related-to-property": [
                            {
                                "property-key": "tenant.tenant-name",
                                "property-value": "onap-dublin-daily-vnfs",
                            }
                        ],
                    }
                ]
            },
        },
        {"service-type": "ims"},
    ]
}

SUBSCRIPTION_TYPES_LIST_TEST = {
    "service-subscription": [
        {
            "service-type": "test",
            "resource-version": "1562591478146",
            "relationship-list": {
                "relationship": [
                    {
                        "related-to": "tenant",
                        "relationship-label": "org.onap.relationships.inventory.Uses",
                        "related-link": "/aai/v16/cloud-infrastructure/cloud-regions/cloud-region/OPNFV/RegionOne/tenants/tenant/4bdc6f0f2539430f9428c852ba606808",
                        "relationship-data": [
                            {
                                "relationship-key": "cloud-region.cloud-owner",
                                "relationship-value": "OPNFV",
                            },
                            {
                                "relationship-key": "cloud-region.cloud-region-id",
                                "relationship-value": "RegionOne",
                            },
                            {
                                "relationship-key": "tenant.tenant-id",
                                "relationship-value": "4bdc6f0f2539430f9428c852ba606808",
                            },
                        ],
                        "related-to-property": [
                            {
                                "property-key": "tenant.tenant-name",
                                "property-value": "onap-dublin-daily-vnfs",
                            }
                        ],
                    }
                ]
            },
        },
        {"service-type": "ims"},
    ]
}

SUBSCRIPTION_ITERATION = [
    {
        "service_type": "test2",
        "resource_version": "1562591478146"
    },
    {"service_type": "ims"}
]

SUBSCRIPTION_ITERATION_TEST = [
    {
        "service_type": "test",
        "resource_version": "1562591478146"
    },
    {"service_type": "ims"}
]

TENANT_TEST = {
    "tenant": [
        {
            "tenant-id": "4bdc6f0f2539430f9428c852ba606808",
            "tenant-name": "myTenant",
            "resource-version": "1562591004273",
            "relationship-list": {
                "relationship": [
                    {
                        "related-to": "service-subscription",
                        "relationship-label": "org.onap.relationships.inventory.Uses",
                        "related-link": "/aai/v16/business/customers/customer/generic/service-subscriptions/service-subscription/freeradius",
                        "relationship-data": [
                            {
                                "relationship-key": "customer.global-customer-id",
                                "relationship-value": "generic",
                            },
                            {
                                "relationship-key": "service-subscription.service-type",
                                "relationship-value": "freeradius",
                            },
                        ],
                    },
                    {
                        "related-to": "service-subscription",
                        "relationship-label": "org.onap.relationships.inventory.Uses",
                        "related-link": "/aai/v16/business/customers/customer/generic/service-subscriptions/service-subscription/ims",
                        "relationship-data": [
                            {
                                "relationship-key": "customer.global-customer-id",
                                "relationship-value": "generic",
                            },
                            {
                                "relationship-key": "service-subscription.service-type",
                                "relationship-value": "ims",
                            },
                        ],
                    },
                    {
                        "related-to": "service-subscription",
                        "relationship-label": "org.onap.relationships.inventory.Uses",
                        "related-link": "/aai/v16/business/customers/customer/generic/service-subscriptions/service-subscription/ubuntu16",
                        "relationship-data": [
                            {
                                "relationship-key": "customer.global-customer-id",
                                "relationship-value": "generic",
                            },
                            {
                                "relationship-key": "service-subscription.service-type",
                                "relationship-value": "ubuntu16",
                            },
                        ],
                    },
                ]
            },
        }
    ]
}

SERVICES_LIST = {
    'resources': [
        {
            "uuid": "3adf00f2-ce12-4f76-a8ac-03fff776116f",
            "invariantUUID": "41b9a64c-783f-425e-aab1-fd4050ba6920",
            "name": "nginxk8s01",
            "version": "1.0", 
            "toscaModelURL": "/sdc/v1/catalog/services/3adf00f2-ce12-4f76-a8ac-03fff776116f/toscaModel",
            "category": "Network Service", 
            "lifecycleState":"CERTIFIED", 
            "lastUpdaterUserId": "cs0008", 
            "distributionStatus":"DISTRIBUTED"
        },
        {
            "uuid": "726ce288-da54-4aa9-bc26-cd20f900f518", 
            "invariantUUID": "0054e502-2075-4b28-b914-19cbaf14c518",
            "name": "ubuntu16test",
            "version": "1.0",
            "toscaModelURL": "/sdc/v1/catalog/services/726ce288-da54-4aa9-bc26-cd20f900f518/toscaModel", 
            "category": "Network Service",
            "lifecycleState": "CERTIFIED",
            "lastUpdaterUserId":"cs0008", 
            "distributionStatus":"DISTRIBUTED"
        }
    ]
}
def test_init_with_args():
    """Check init with args."""
    instantiate = Instantiate(service_name= "test")
    # assert isinstance(vendor, SdcElement)
    assert instantiate.service_name == "test"
    

def test_init_without_args1():
    """Check init without arg service_name"""
    with pytest.raises(ValueError):
        instantiate = Instantiate()

@mock.patch.object(Customer, 'send_message_json')
def test_create_customer1(mock_get):
    service = Instantiate(service_name= "test")
    mock_get.return_value = CUSTOMERS
    customer = service.create_customer("generic")
    assert customer.subscriber_name == "generic"

@mock.patch.object(Customer, 'send_message_json')
@mock.patch.object(Customer, 'create')
def test_create_customer2(mock_create, mock_get):
    service = Instantiate(service_name= "test")
    mock_get.return_value = CUSTOMERS
    customer = service.create_customer("toto")
    assert customer
    mock_create.assert_called_once()


@mock.patch.object(Customer, 'send_message_json')
@mock.patch.object(Customer, 'subscribe_service')
def test_declare_service_subscription1(mock_subscribe, mock_svc):
    instanc = Instantiate(service_name= "test")
    service = Service(name="test")       
    
    customer = Customer("generic", "generic", "INFRA", "1581510772967")
    mock_svc.return_value = SUBSCRIPTION_TYPES_LIST
    service_subs = instanc.declare_service_subscription(customer, service)
    assert service_subs
    mock_subscribe.assert_called_once()
    
@mock.patch.object(Customer, 'send_message_json')
def test_declare_service_subscription2(mock_svc):
    instanc = Instantiate(service_name= "test")
    service = Service(name="test")       
    
    customer = Customer("generic", "generic", "INFRA", "1581510772967")
    mock_svc.return_value = SUBSCRIPTION_TYPES_LIST_TEST
    service_subs = instanc.declare_service_subscription(customer, service)
    assert service_subs

@mock.patch.object(AaiElement, 'send_message_json')
def test_check_tenant_exists(mock_cloud):
    instanc = Instantiate(service_name= "test")
    cloud_region = CloudRegion(
        cloud_owner="OPNFV",
        cloud_region_id="RegionOne",
        cloud_type="openstack",
        owner_defined_type="N/A",
        cloud_region_version="pike",
        identity_url=None,
        cloud_zone="OPNFV LaaS",
        complex_name="Cruguil",
        sriov_automation=None,
        cloud_extra_info=None,
        upgrade_cycle=None,
        orchestration_disabled=False,
        in_maint=False,
        resource_version=None,
    )
    tenant_name = "myTenant"
    mock_cloud.return_value = TENANT_TEST
    check_tenant = instanc.check_tenant_exists(cloud_region, tenant_name)
    assert check_tenant

    tenant_name = "myTenantError"
    mock_cloud.return_value = TENANT_TEST
    with pytest.raises(SystemExit):
        check_tenant = instanc.check_tenant_exists(cloud_region, tenant_name)

def test_get_vnf_paramters():
    instanc = Instantiate(service_name= "ubuntu16test")
    vnf_parameters = instanc.get_vnf_parameters("ubuntu16test")
    assert vnf_parameters

@mock.patch.object(Service, 'get_all')
def test_find_service_sdc(mock_get):
    instanc = Instantiate(service_name= "ubuntu16test")
    service = Service("ubuntu16test")
    service.unique_uuid = "1234"
    service.identifier = "12345"
    service.name = "ubuntu16test"
    mock_get.return_value = [service]
    service_found = instanc.find_service_sdc("ubuntu16test")
    assert service_found

@mock.patch.object(Service, '_check_distributed')
def test_check_service_distribution(mock_distri):
    instanc = Instantiate(service_name= "ubuntu16test")
    service = Service("ubuntu16test")
    service.unique_uuid = "1234"
    service.identifier = "12345"
    service.name = "ubuntu16test"
    service.distribution_status = ""
    service._distributed = True
    instanc.check_service_distribution(service, 1, 1)

@mock.patch.object(Service, '_check_distributed')
def test_check_service_distribution_error(mock_distri):
    instanc = Instantiate(service_name= "ubuntu16test")
    service = Service("ubuntu16test")
    service.unique_uuid = "1234"
    service.identifier = "12345"
    service.name = "ubuntu16test"
    service.distribution_status = ""
    service._distributed = False
    with pytest.raises(SystemExit):
        instanc.check_service_distribution(service, 1, 1)


@mock.patch.object(OnapService, 'send_message_json')
def test_check_service_instance_exists(mock_svc):
    instanc = Instantiate(service_name= "ubuntu16test")
    service = Service("ubuntu16test")
    service.name = "ubuntu16test"
    customer = Customer("generic", "generic", "INFRA", "1581510772967")
    service_subscription = ServiceSubscription(
        customer=customer,
        service_type="ubuntu16test",
        resource_version="62591478146"
    )
    mock_svc.return_value = {
        "service-instance":[
            {
                "service-instance-id": "7eb6d7e8-9631-4465-91ef-dfe7300cc21d",
                "service-instance-name": "ubuntu16test",
                "environment-context": "General_Revenue-Bearing",
                "workload-context": "Production",
                "model-invariant-id": "b0f6f6a2-4fa5-4535-89cd-3a6b56032057",
                "model-version-id": "aa675c33-82d6-44f7-9f11-7f4f3125fb33",
                "resource-version": "1591879760051",
                "selflink":" restconf/config/GENERIC-RESOURCE-API:services/service/7eb6d7e8-9631-4465-91ef-dfe7300cc21d/service-data/service-topology/",
                "orchestration-status": "Active",
                "relationship-list": {
                    "relationship": [
                        {
                            "related-to": "owning-entity",
                            "relationship-label": "org.onap.relationships.inventory.BelongsTo",
                            "related-link": "/aai/v16/business/owning-entities/owning-entity/324a7544-577f-4840-9a8f-cb44ccf3c6ac",
                            "relationship-data": [
                                {
                                    "relationship-key": "owning-entity.owning-entity-id",
                                    "relationship-value": "324a7544-577f-4840-9a8f-cb44ccf3c6ac"
                                }
                            ]
                        },
                        {
                            "related-to": "project",
                            "relationship-label": "org.onap.relationships.inventory.Uses",
                            "related-link": "/aai/v16/business/projects/project/SDKTest-project",
                            "relationship-data": [
                                {
                                    "relationship-key": "project.project-name",
                                    "relationship-value": "SDKTest-project"
                                }
                            ]
                        }
                    ]
                }
            }             
        ]
    }    
    instanc.check_service_instance_exists(
        service_subscription,
        "ubuntu16test")

@mock.patch.object(Instantiate, 'check_service_instance_exists')
def test_check_service_instantiation(mock_svc):
    instanc = Instantiate(service_name= "ubuntu16test")
    customer = Customer("generic", "generic", "INFRA", "1581510772967")
    service_subscription = ServiceSubscription(
        customer=customer,
        service_type="ubuntu16test",
        resource_version="62591478146"
    )
    mock_svc.return_value = None
    with pytest.raises(SystemExit):
        instanc.check_service_instantiation(
            service_subscription,
            "ubuntu16test")

def test_check_service_instance_active():
    instanc = Instantiate(service_name= "ubuntu16test")
    customer = Customer("generic", "generic", "INFRA", "1581510772967")
    service_subscription = ServiceSubscription(
        customer=customer,
        service_type="ubuntu16test",
        resource_version="62591478146"
    )
    service_instance = ServiceInstance(
        service_subscription = service_subscription,
        instance_id = "1234",
        instance_name = "ubuntu16test",
        orchestration_status = "Wait")
    instanc.check_service_instance_active(service_instance, 1, 1)

@mock.patch.object(OnapService, 'send_message_json')
def test_instantiate_service1(mock_svc):
    instanc = Instantiate(service_name= "ubuntu16test", instance_name= "test")
    service = Service("ubuntu16test")
    service.name = "ubuntu16test"
    customer = Customer("generic", "generic", "INFRA", "1581510772967")
    service_subscription = ServiceSubscription(
        customer=customer,
        service_type="ubuntu16test",
        resource_version="62591478146"
    )
    cloud_region = CloudRegion(
        "test_owner",
        "test_cloud_region",
        orchestration_disabled=True,
        in_maint=False
    )
    tenant = Tenant("test_cloud_region", "IdTenant", "TenantName", "TenantCtxt", "1.0")
    owning_entity = AaiOwningEntity("b3dcdbb0-edae-4384-b91e-2f114472520c", "test", "1.0")
    project = Project("SDKTest-project")
    mock_svc.return_value = {
        "service-instance":[
            {
                "service-instance-id": "7eb6d7e8-9631-4465-91ef-dfe7300cc21d",
                "service-instance-name": "test",
                "environment-context": "General_Revenue-Bearing",
                "workload-context": "Production",
                "model-invariant-id": "b0f6f6a2-4fa5-4535-89cd-3a6b56032057",
                "model-version-id": "aa675c33-82d6-44f7-9f11-7f4f3125fb33",
                "resource-version": "1591879760051",
                "selflink":" restconf/config/GENERIC-RESOURCE-API:services/service/7eb6d7e8-9631-4465-91ef-dfe7300cc21d/service-data/service-topology/",
                "orchestration-status": "Active",
                "relationship-list": {
                    "relationship": [
                        {
                            "related-to": "owning-entity",
                            "relationship-label": "org.onap.relationships.inventory.BelongsTo",
                            "related-link": "/aai/v16/business/owning-entities/owning-entity/324a7544-577f-4840-9a8f-cb44ccf3c6ac",
                            "relationship-data": [
                                {
                                    "relationship-key": "owning-entity.owning-entity-id",
                                    "relationship-value": "324a7544-577f-4840-9a8f-cb44ccf3c6ac"
                                }
                            ]
                        },
                        {
                            "related-to": "project",
                            "relationship-label": "org.onap.relationships.inventory.Uses",
                            "related-link": "/aai/v16/business/projects/project/SDKTest-project",
                            "relationship-data": [
                                {
                                    "relationship-key": "project.project-name",
                                    "relationship-value": "SDKTest-project"
                                }
                            ]
                        }
                    ]
                }
            }             
        ]
    }    
    instanc.instantiate_service(
        instanc.instance_name,
        service,
        service_subscription,
        cloud_region,
        tenant,
        customer,
        owning_entity,
        project,
        1, 1, 1)

@mock.patch.object(ServiceInstantiation, 'instantiate_so_ala_carte')
@mock.patch.object(Instantiate, 'check_service_instance_active')
@mock.patch.object(Instantiate, 'check_service_instantiation')
@mock.patch.object(Instantiate, 'check_service_instance_exists')
@mock.patch.object(OnapService, 'send_message_json')
def test_instantiate_service2(mock_svc, mock_check, mock_instantiation, mock_active, mock_instant):
    instanc = Instantiate(service_name= "ubuntu16test")
    service = Service("ubuntu16test")
    service.name = "ubuntu16test"
    customer = Customer("generic", "generic", "INFRA", "1581510772967")
    service_subscription = ServiceSubscription(
        customer=customer,
        service_type="ubuntu16test",
        resource_version="62591478146"
    )
    cloud_region = CloudRegion(
        "test_owner",
        "test_cloud_region",
        orchestration_disabled=True,
        in_maint=False
    )
    tenant = Tenant("test_cloud_region", "IdTenant", "TenantName", "TenantCtxt", "1.0")
    owning_entity = AaiOwningEntity("b3dcdbb0-edae-4384-b91e-2f114472520c", "test", "1.0")
    project = Project("SDKTest-project")
    mock_instantiation.return_value = ServiceInstance(
        service_subscription = service_subscription,
        instance_id = "1234",
        instance_name = "ubuntu16test",
        orchestration_status = "Active")
    mock_active.return_value = True
    mock_check.return_value = None
    mock_svc.return_value = {
        "service-instance":[
            {
                "service-instance-id": "7eb6d7e8-9631-4465-91ef-dfe7300cc21d",
                "service-instance-name": "ubuntu16test",
                "environment-context": "General_Revenue-Bearing",
                "workload-context": "Production",
                "model-invariant-id": "b0f6f6a2-4fa5-4535-89cd-3a6b56032057",
                "model-version-id": "aa675c33-82d6-44f7-9f11-7f4f3125fb33",
                "resource-version": "1591879760051",
                "selflink": "restconf/config/GENERIC-RESOURCE-API:services/service/7eb6d7e8-9631-4465-91ef-dfe7300cc21d/service-data/service-topology/",
                "orchestration-status": "Active",
                "relationship-list": {
                    "relationship": [
                        {
                            "related-to": "owning-entity",
                            "relationship-label": "org.onap.relationships.inventory.BelongsTo",
                            "related-link": "/aai/v16/business/owning-entities/owning-entity/324a7544-577f-4840-9a8f-cb44ccf3c6ac",
                            "relationship-data": [
                                {
                                    "relationship-key": "owning-entity.owning-entity-id",
                                    "relationship-value": "324a7544-577f-4840-9a8f-cb44ccf3c6ac"
                                }
                            ]
                        },
                        {
                            "related-to": "project",
                            "relationship-label": "org.onap.relationships.inventory.Uses",
                            "related-link": "/aai/v16/business/projects/project/SDKTest-project",
                            "relationship-data": [
                                {
                                    "relationship-key": "project.project-name",
                                    "relationship-value": "SDKTest-project"
                                }
                            ]
                        }
                    ]
                }
            }             
        ]
    }
    instanc.instantiate_service(
        instanc.instance_name,
        service,
        service_subscription,
        cloud_region,
        tenant,
        customer,
        owning_entity,
        project,
        1, 1, 1)
    mock_instant.assert_called_once()

@mock.patch.object(ServiceInstantiation, 'instantiate_so_ala_carte')
@mock.patch.object(Instantiate, 'check_service_instance_active')
@mock.patch.object(Instantiate, 'check_service_instantiation')
@mock.patch.object(Instantiate, 'check_service_instance_exists')
@mock.patch.object(OnapService, 'send_message_json')
def test_instantiate_service3(mock_svc, mock_check, mock_instantiation, mock_active, mock_instant):
    instanc = Instantiate(service_name= "ubuntu16test")
    service = Service("ubuntu16test")
    service.name = "ubuntu16test"
    customer = Customer("generic", "generic", "INFRA", "1581510772967")
    service_subscription = ServiceSubscription(
        customer=customer,
        service_type="ubuntu16test",
        resource_version="62591478146"
    )
    cloud_region = CloudRegion(
        "test_owner",
        "test_cloud_region",
        orchestration_disabled=True,
        in_maint=False
    )
    tenant = Tenant("test_cloud_region", "IdTenant", "TenantName", "TenantCtxt", "1.0")
    owning_entity = AaiOwningEntity("b3dcdbb0-edae-4384-b91e-2f114472520c", "test", "1.0")
    project = Project("SDKTest-project")
    mock_instantiation.return_value = ServiceInstance(
        service_subscription = service_subscription,
        instance_id = "1234",
        instance_name = "ubuntu16test",
        orchestration_status = "Active")
    mock_active.return_value = False
    mock_check.return_value = None
    mock_svc.return_value = {
        "service-instance":[
            {
                "service-instance-id": "7eb6d7e8-9631-4465-91ef-dfe7300cc21d",
                "service-instance-name": "ubuntu16test",
                "environment-context": "General_Revenue-Bearing",
                "workload-context": "Production",
                "model-invariant-id": "b0f6f6a2-4fa5-4535-89cd-3a6b56032057",
                "model-version-id": "aa675c33-82d6-44f7-9f11-7f4f3125fb33",
                "resource-version": "1591879760051",
                "selflink": "restconf/config/GENERIC-RESOURCE-API:services/service/7eb6d7e8-9631-4465-91ef-dfe7300cc21d/service-data/service-topology/",
                "orchestration-status": "Active",
                "relationship-list": {
                    "relationship": [
                        {
                            "related-to": "owning-entity",
                            "relationship-label": "org.onap.relationships.inventory.BelongsTo",
                            "related-link": "/aai/v16/business/owning-entities/owning-entity/324a7544-577f-4840-9a8f-cb44ccf3c6ac",
                            "relationship-data": [
                                {
                                    "relationship-key": "owning-entity.owning-entity-id",
                                    "relationship-value": "324a7544-577f-4840-9a8f-cb44ccf3c6ac"
                                }
                            ]
                        },
                        {
                            "related-to": "project",
                            "relationship-label": "org.onap.relationships.inventory.Uses",
                            "related-link": "/aai/v16/business/projects/project/SDKTest-project",
                            "relationship-data": [
                                {
                                    "relationship-key": "project.project-name",
                                    "relationship-value": "SDKTest-project"
                                }
                            ]
                        }
                    ]
                }
            }             
        ]
    }
    with pytest.raises(SystemExit):
        instanc.instantiate_service(
            service,
            service_subscription,
            cloud_region,
            tenant,
            customer,
            owning_entity,
            project,
            1, 1, 1)
        mock_instant.assert_called_once()


@mock.patch.object(ServiceSubscription, "sdc_service")
@mock.patch.object(ServiceInstance, "send_message_json")
@mock.patch.object(VnfInstance, "create_from_api_response")
@mock.patch.object(ServiceInstance, 'add_vnf')
@mock.patch.object(OrchestrationRequest, "send_message_json")
def test_add_vnf_to_service1(mock_orch, mock_add_vnf, mock_vnf_api, mock_service, mock_svc):
    instanc = Instantiate(service_name= "ubuntu16test")
    service = Service("test_service")
    service.unique_uuid = "xxxx"
    service.identifier = "xxxx"
    service.name = "test_service"
    customer = Customer("generic", "generic", "INFRA", "1581510772967")
    service_subscription = ServiceSubscription(
        customer=customer,
        service_type="ubuntu16test",
        resource_version="62591478146"
    )
    service_instance = ServiceInstance(
        service_subscription = service_subscription,
        instance_id = "1234",
        instance_name = "ubuntu16test",
        orchestration_status = "Active")
    platform = Platform("SDKTest-PLATFORM")
    lob = LineOfBusiness("SDKTest-BusinessLine")
    vnftest = Vnf(
        name = "vnftest",
        node_template_type = "xxx",
        metadata = "xxx",
        properties = "xxx",
        capabilities = "yyy"
    )
    mock_svc.return_value = service
    mock_svc.vnfs = [vnftest]

    mock_service.return_value = {
        "relationship": [
            {
                "related-to": "generic-vnf",
                "relationship_label": "anything",
                "related_link": "test_relationship_related_link",
                "relationship_data": []
            }
        ]
    }
    mock_vnf_api.return_value = VnfInstance(
        service_instance = service_instance,
        vnf_id = "xxx",
        vnf_type = "network",
        in_maint = False,
        is_closed_loop_disabled = False,
        vnf_name = "vnftest"
    )

    mock_add_vnf.return_value = VnfInstantiation(
        name = "vnftest",
        request_id = "xxxx",
        instance_id = "xxxx",
        line_of_business = lob,
        platform = platform,
        vnf = vnftest
    )
    mock_orch.return_value = {
        "request": {
            "requestStatus": {
                "requestState": "COMPLETE"
            }
        }
    }
    instanc.add_vnf_to_service(service_instance, platform, lob, 1)

@mock.patch.object(ServiceSubscription, "sdc_service")
@mock.patch.object(ServiceInstance, "send_message_json")
@mock.patch.object(VnfInstance, "create_from_api_response")
@mock.patch.object(ServiceInstance, 'add_vnf')
@mock.patch.object(OrchestrationRequest, "send_message_json")
def test_add_vnf_to_service2(mock_orch, mock_add_vnf, mock_vnf_api, mock_service, mock_svc):
    instanc = Instantiate(service_name= "ubuntu16test")
    service = Service("test_service")
    service.unique_uuid = "xxxx"
    service.identifier = "xxxx"
    service.name = "test_service"
    customer = Customer("generic", "generic", "INFRA", "1581510772967")
    service_subscription = ServiceSubscription(
        customer=customer,
        service_type="ubuntu16test",
        resource_version="62591478146"
    )
    service_instance = ServiceInstance(
        service_subscription = service_subscription,
        instance_id = "1234",
        instance_name = "ubuntu16test",
        orchestration_status = "Active")
    platform = Platform("SDKTest-PLATFORM")
    lob = LineOfBusiness("SDKTest-BusinessLine")
    vnftest = Vnf(
        name = "vnftest",
        node_template_type = "xxx",
        metadata = "xxx",
        properties = "xxx",
        capabilities = "yyy"
    )
    mock_svc.return_value = service
    mock_svc.vnfs = [vnftest]

    mock_service.return_value = {
        "relationship": [
            {
                "related-to": "generic-vnf",
                "relationship_label": "anything",
                "related_link": "test_relationship_related_link",
                "relationship_data": []
            }
        ]
    }
    mock_vnf_api.return_value = VnfInstance(
        service_instance = service_instance,
        vnf_id = "xxx",
        vnf_type = "network",
        in_maint = False,
        is_closed_loop_disabled = False,
        vnf_name = "vnftest2"
    )

    mock_add_vnf.return_value = VnfInstantiation(
        name = "vnftest",
        request_id = "xxxx",
        instance_id = "xxxx",
        line_of_business = lob,
        platform = platform,
        vnf = vnftest
    )
    mock_orch.side_effect = [
        {
            "request": {
                "requestStatus": {
                    "requestState": "IN_PROGRESS"
                }
            }
        },
        {
            "request": {
                "requestStatus": {
                    "requestState": "COMPLETE"
                }
            }
        }
    ]


    instanc.add_vnf_to_service(service_instance, platform, lob, 1)
