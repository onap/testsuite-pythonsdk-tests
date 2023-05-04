import subprocess
username = subprocess.check_output(['whoami']).strip().decode('utf-8')
subprocess.run(['sudo','chown', username, '/var/lib/'])
subprocess.run(['sudo','chown',"root:root", '/var/lib'])
from onaptests.scenario.status import Status
status=Status()
status.run()