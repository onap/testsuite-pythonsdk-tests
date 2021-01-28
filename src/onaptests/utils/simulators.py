"""Standard functions for the simulator wrapper."""
from onaptests.configuration.settings import CWD

def get_local_dir():
    """Get the default path for helm charts."""
    return CWD / 'src' / 'onaptests' / 'templates' / 'helm_charts'
