import os
import subprocess

def uninstall_prometheus_node_exporter(location, silent, retries):
    location = os.path.expanduser(location)

    stop_prometheus_node_exporter(True)

    if isfile(join(location, 'node_exporter')):
        rm(location, ignore_errors=True)
    subprocess.call('sudo rm -rf /usr/bin/node_exporter /etc/systemd/system/node_exporter.service', **get_subprocess_kwargs(silent))
    return True


def uninstall_prometheus_admin(location, silent, retries):
    location = os.path.expanduser(location)
    if isfile(join(location, 'prometheus')) and isfile('/usr/bin/prometheus') and isfile('/etc/systemd/system/prometheus.service'):
        rm(location, ignore_errors=True)
    subprocess.call('sudo rm -rf /usr/bin/prometheus /etc/systemd/system/prometheus.service', **get_subprocess_kwargs(silent))
    return True