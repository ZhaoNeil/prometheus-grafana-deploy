import subprocess


def stop_prometheus_node_exporter(silent):
    if not isfile('/etc/systemd/system/node_exporter.service'):
        return False # We have no node daemon installed.
    if subprocess.call('sudo systemctl stop node_exporter', **get_subprocess_kwargs(silent)) != 0:
        return False
    return subprocess.call('sudo systemctl disable node_exporter', **get_subprocess_kwargs(silent)) == 0

def stop_prometheus_admin(silent):
    if not isfile('/etc/systemd/system/prometheus.service'):
        return False # We have no node daemon installed.
    if subprocess.call('sudo systemctl stop prometheus', **get_subprocess_kwargs(silent)) != 0:
        return False
    return subprocess.call('sudo systemctl disable prometheus', **get_subprocess_kwargs(silent)) == 0