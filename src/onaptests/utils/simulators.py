"""Standard functions for the simulator wrapper."""
from importlib.resources import path

def get_local_dir():
    """Get the default path for helm charts.

    Returns:
        chart_directory (Path):
        local helm chart folder relative to the package.
    """
    with path('onaptests', 'templates') as templates:
        chart_directory = templates / 'helm_charts'
    return chart_directory
