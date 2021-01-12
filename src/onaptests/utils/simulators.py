"""Utility functions to help manage docker configuration files."""
import os
from typing import Dict
import yaml


def get_config(filename: str) -> Dict:
    """Read a config YAML file."""
    config = None
    absolute_path = f"{os.path.dirname(os.path.realpath(__file__))}/../steps/simulator/{filename}"
    with open(absolute_path, "r") as ymlfile:
        config = yaml.safe_load(ymlfile)
    return config
