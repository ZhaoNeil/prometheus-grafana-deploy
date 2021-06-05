import subprocess


def start_prometheus_node_exporter(location, silent):
    if not isfile('/etc/systemd/system/node_exporter.service'):
        return False # We have no node daemon installed.
    if subprocess.call('sudo systemctl start node_exporter', **get_subprocess_kwargs(silent)) != 0:
        return False
    return subprocess.call('sudo systemctl enable node_exporter', **get_subprocess_kwargs(silent)) == 0

def start_prometheus_admin(location, hostlist, silent):
    if not isfile('/etc/systemd/system/prometheus.service'):
        return False # We have no node daemon installed.
    location = os.path.expanduser(location)
    if not isdir(location):
        mkdir(location, exist_ok=True)
    configfile = join(location, 'config.yml')
    with open(configfile, 'w') as f:
        f.write('''
global:
  scrape_interval: 15s

scrape_configs:
- job_name: node
  static_configs:
  - targets: [
{}
  ]
'''.format('\n'.join('    {},'.format(host) for host in hostlist)))
    if subprocess.call('sudo systemctl start prometheus', **get_subprocess_kwargs(silent)) != 0:
        return False
    return subprocess.call('sudo systemctl enable prometheus', **get_subprocess_kwargs(silent)) == 0
