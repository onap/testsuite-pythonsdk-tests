"""Utility functions that invoke operations of simulator script."""
import os
import sys
from ipaddress import ip_address
from typing import Optional
from decorator import decorator
import docker
from onaptests.integration.test.mocks.masspnfsim.MassPnfSim import (
    MassPnfSim, get_parser
)


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

def get_default_args() -> None:
    """Prepare default arguments for required operations.

    Returns:
        args (argparse.Namespace): default arguments.

    """
    parser = get_parser()
    args = parser.parse_args('')
    return args

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
    repo_names = [
        "nexus3.onap.org:10003/onap/masspnf-simulator",
        "openjdk",
        "atmoz/sftp",
        "panubo/vsftpd"
        ]

    for repo_name in repo_names:
        image_tags = client.images.list(repo_name)
        for obj in image_tags:
            client.images.remove(obj.id, force=True)

@chdir
def bootstrap_simulator(**kwargs) -> None:
    """Setup simulator(s) repo, data and configs."""
    args = get_default_args()

    # collect settings that will be placed in the simulator directory
    vesprotocol=kwargs.get('vesprotocol', "http")
    vesip=kwargs.get('vesip', "")
    vesport=kwargs.get('vesport', "")
    vesresource=kwargs.get('vesresource', "")
    vesversion=kwargs.get('vesversion', "")
    urlves = f"{vesprotocol}://{vesip}:{vesport}/{vesresource}/{vesversion}"

    # assign to simulator's arguments
    args.count = kwargs.get('count', 1)
    args.urlves = urlves
    args.ipstart = ip_address(kwargs.get('ipstart', ''))
    args.ipfileserver = kwargs.get('ipfileserver', '')
    args.typefileserver = kwargs.get('typefileserver', '')
    args.user = kwargs.get('user', '')
    args.password = kwargs.get('password', '')

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
    trigger = getattr(MassPnfSim(), "trigger")
    args = get_default_args()
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
