"""Utility functions that invoke operations of simulator script."""
import os
import sys
import time
import yaml
from ipaddress import ip_address
from typing import Dict, Optional
from decorator import decorator
import docker
from onaptests.integration.test.mocks.masspnfsim.MassPnfSim import (
    MassPnfSim, get_parser
)

def get_config() -> Dict:
    """Read a config YAML file."""
    config = None
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f"{dir_path}/pnf_config.yaml", "r") as ymlfile:
        config = yaml.load(ymlfile)
    return config

def get_default_args() -> None:
    """Prepare default arguments for required operations.

    Returns:
        args (argparse.Namespace): default arguments.

    """
    parser = get_parser()
    args = parser.parse_args('')
    return args

def switch_workdir(back_pwd: str = None) -> Optional[str]:
    """Switch work directory temporarily for PNF simulator operations.

    When `back_pwd` path is provided, it means go back tp the repository
    you came from.

    Arguments:
        back_pwd: path to go back to.

    Returns:
        old_pwd (str): previous path.

    """
    sim_file_path = sys.modules[MassPnfSim.__module__].__file__
    sim_dir_path = os.path.dirname(sim_file_path)

    old_pwd = os.getcwd()

    if not back_pwd:
        curr_pwd = sim_dir_path
    else:
        curr_pwd = back_pwd

    os.chdir(curr_pwd)
    return old_pwd

@decorator
def chdir(func, *args, **kwargs):
    """Switches to and from the simulator workspace."""
    old_pwd = switch_workdir()
    ret = func(*args, **kwargs)
    switch_workdir(old_pwd)
    return ret

@chdir
def build_image() -> None:
    """Build simulator image."""
    build = getattr(MassPnfSim(), "build")
    args = get_default_args()
    build(args)

@chdir
def remove_image() -> None:
    """Remove simulator image(s)."""
    client = docker.from_env()
    sim_image_name = "nexus3.onap.org:10003/onap/masspnf-simulator"
    images = client.images.list(sim_image_name)
    for obj in images:
        client.images.remove(obj.id, force=True)

@chdir
def bootstrap_simulator() -> None:
    """Setup simulator(s) repo, data and configs."""
    args = get_default_args()
    config = get_config()

    # collect settings that will be placed in the simulator directory
    vesprotocol = config["setup"].get('vesprotocol', "http")
    vesip = config["setup"].get('vesip', "")
    vesport = config["setup"].get('vesport', "")
    vesresource = config["setup"].get('vesresource', "")
    vesversion = config["setup"].get('vesversion', "")

    urlves = f"{vesprotocol}://{vesip}:{vesport}/{vesresource}/{vesversion}"

    # assign to simulator's arguments
    args.count = config["setup"].get('count', 1)
    args.urlves = urlves
    args.ipstart = ip_address(config["setup"].get('ipstart', ''))
    args.ipfileserver = config["setup"].get('ipfileserver', '')
    args.typefileserver = config["setup"].get('typefileserver', '')
    args.user = config["setup"].get('user', '')
    args.password = config["setup"].get('password', '')

    # bootstrap with assigned arguments
    bootstrap = getattr(MassPnfSim(), "bootstrap")
    bootstrap(args)

@chdir
def run_container() -> None:
    """Run simulator container(s)."""
    start = getattr(MassPnfSim(), "start")
    args = get_default_args()
    start(args)

@chdir
def register() -> None:
    """Send an event to VES.

    Use time.sleep(seconds) if registering with VES right after run_container().
    Containers take a few seconds to run properly. Normally 5 seconds should be
    enough.

    """
    time.sleep(5)
    config = get_config()
    trigger = getattr(MassPnfSim(), "trigger")
    args = get_default_args()

    args.user = config['setup'].get('user', '')
    args.password = config['setup'].get('password', '')

    custom_data = config['data']
    if custom_data:
        args.data = custom_data

    trigger(args)

@chdir
def stop_container() -> None:
    """Stop simulator container(s)."""
    stop = getattr(MassPnfSim(), "stop")
    args = get_default_args()
    stop(args)

@chdir
def remove_simulator() -> None:
    """Remove simulator container(s)."""
    clean = getattr(MassPnfSim(), "clean")
    args = get_default_args()
    clean(args)
