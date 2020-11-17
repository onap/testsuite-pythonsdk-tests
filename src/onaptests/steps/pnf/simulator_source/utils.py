import docker
from ipaddress import ip_address

from onaptests.steps.pnf.simulator_source.mass_pnf_sim import (
    MassPnfSim, get_parser
)

def get_default_args():
    """Prepare default arguments for required operations."""
    parser = get_parser()
    args = parser.parse_args('')
    return args

def build_image():
    """Build simulator image."""
    build = getattr(MassPnfSim(), "build")
    args = get_default_args()
    build(args)

def remove_image():
    """Remove simulator image(s)."""
    client = docker.from_env()
    repo_names = ["nexus3.onap.org:10003/onap/masspnf-simulator", "openjdk"]
    
    for repo_name in repo_names:
        image_tags = client.images.list(repo_name)
        for obj in image_tags:
            client.images.remove(obj.id, force=True)

def bootstrap_simulator(**kwargs):
    """Setup simulator(s) repo, data and configs."""
    args = get_default_args()

    vesprotocol=kwargs.get('vesprotocol', "http")
    vesip=kwargs.get('vesip', "")
    vesport=kwargs.get('vesport', "")
    vesresource=kwargs.get('vesresource', "")
    vesversion=kwargs.get('vesversion', "")
    urlves = f"{vesprotocol}://{vesip}:{vesport}/{vesresource}/{vesversion}"

    args.count = kwargs.get('count', 1)
    args.urlves = urlves
    args.ipstart = ip_address(kwargs.get('ipstart', ''))
    args.ipfileserver = kwargs.get('ipfileserver', '')
    args.typefileserver = kwargs.get('typefileserver', '')
    args.user = kwargs.get('user', '')
    args.password = kwargs.get('password', '')

    bt = getattr(MassPnfSim(), "bootstrap")
    bt(args)

def run_container():
    """Run simulator container(s)."""
    start = getattr(MassPnfSim(), "start")
    args = get_default_args()
    start(args)

def register():
    """Send an event to VES.
    
    Use time.sleep(seconds) if registering with VES right after run_container().
    Containers take a few seconds to run properly. Normally 5 seconds should be enough.
    
    """
    trigger = getattr(MassPnfSim(), "trigger")

    args = get_default_args()
    trigger(args)

def stop_container():
    """Stop simulator container(s)."""
    stop = getattr(MassPnfSim(), "stop")
    args = get_default_args()
    stop(args)

def remove_simulator():
    """Remove simulator container(s)."""
    clean = getattr(MassPnfSim(), "clean")
    args = get_default_args()
    clean(args)
