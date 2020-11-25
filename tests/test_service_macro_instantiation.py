import pytest
from unittest import mock

from onaptests.steps.instantiate.service_macro import (
    YamlTemplateServiceMacroInstantiateStep
)

VNFS_PNFS_YAML = './tests/data/service_macro_template_vnfs.yaml'
PNFS_YAML = './tests/data/service_macro_template_pnfs.yaml'


@mock.patch("onaptests.steps.base.BaseStep.add_step")
@mock.patch("onaptests.steps.instantiate.service_macro.settings")
@mock.patch("onaptests.steps.instantiate.service_macro.YamlTemplateServiceOnboardStep")
@mock.patch("onaptests.steps.instantiate.service_macro.ConnectServiceSubToCloudRegionStep")
@mock.patch("onaptests.steps.instantiate.service_macro.CustomerServiceSubscriptionCreateStep")
def test_are_vnfs(CustomerStep, CloudStep, OnboardStep, settings, add_step):

    settings.SERVICE_YAML_TEMPLATE = VNFS_PNFS_YAML
    settings.ONLY_INSTANTIATE = False

    YamlTemplateServiceMacroInstantiateStep()

    CustomerStep.assert_not_called()
    assert add_step.mock_calls == [
        mock.call(OnboardStep()), mock.call(CloudStep())]


@mock.patch("onaptests.steps.base.BaseStep.add_step")
@mock.patch("onaptests.steps.instantiate.service_macro.settings")
@mock.patch("onaptests.steps.instantiate.service_macro.YamlTemplateServiceOnboardStep")
@mock.patch("onaptests.steps.instantiate.service_macro.ConnectServiceSubToCloudRegionStep")
@mock.patch("onaptests.steps.instantiate.service_macro.CustomerServiceSubscriptionCreateStep")
def test_are_pnfs(CustomerStep, CloudStep, OnboardStep, settings, add_step):

    settings.SERVICE_YAML_TEMPLATE = PNFS_YAML
    settings.ONLY_INSTANTIATE = False

    YamlTemplateServiceMacroInstantiateStep()

    CloudStep.assert_not_called()
    assert add_step.mock_calls == [
        mock.call(OnboardStep()), mock.call(CustomerStep())]
