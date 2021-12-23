"""Standard functions for the simulator wrapper."""
import os
from importlib.resources import path
import onaptests


def get_resource_location(relative_path: str):
    return os.path.join(os.path.dirname(os.path.realpath(onaptests.__file__)),
                        relative_path)


def get_local_dir():
    """Get the default path for helm charts.

    Returns:
        chart_directory (Path):
        local helm chart folder relative to the package.
    """
    with path('onaptests', 'templates') as templates:
        chart_directory = templates / 'helm_charts'
    return chart_directory
