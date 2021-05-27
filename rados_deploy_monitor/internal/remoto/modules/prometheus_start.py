import subprocess


def start_prometheus_node_exporter(instal_dir, silent):
    if not isfile('/etc/systemd/system/node_exporter.service'):
        return False # We have no node daemon installed.
    if subprocess.call('sudo systemctl start node_exporter', shell=True) != 0:
        return False
    return subprocess.call('sudo systemctl enable node_exporter', shell=True) == 0

def start_prometheus_admin(instal_dir, hostlist, silent):
    if not isfile('/etc/systemd/system/prometheus.service'):
        return False # We have no node daemon installed.
    configfile = join(instal_dir, 'config.yml')
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
'''.format('\n'.join('    {}'.format(host) for host in hostlist)))
    if subprocess.call('sudo systemctl start prometheus', shell=True) != 0:
        return False
    return subprocess.call('sudo systemctl enable prometheus', shell=True) == 0
