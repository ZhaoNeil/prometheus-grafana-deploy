import os
import subprocess
import tempfile
import urllib.request


def _download_url(location, url, name='unspecified', silent=False, retries=5):
    '''Download a zip from an URL.
    Args:
        url (str): URL zip.
        name (optional str): Name for download to display when reporting errors.
        silent (optional bool): If set,  does not print.
        retries (optional int): Amount of retries before reporting errors.

    Returns:
        `True` on success, `False` otherwise.'''
    with tempfile.TemporaryDirectory() as tmpdir: # We use a tempfile to store the downloaded archive.
        archiveloc = join(tmpdir, url.split('/')[-1])
        if not silent:
            print('Fetching Prometheus node exporter from {}'.format(url))
        for x in range(retries):
            try:
                try:
                    rm(archiveloc)
                except Exception as e:
                    pass
                urllib.request.urlretrieve(url, archiveloc)
                break
            except Exception as e:
                if x == 0:
                    printw('Could not download {}, url={}. Retrying...'.format(name, url))
                elif x == retries-1:
                    printe('Could not download {}, url={}. {}'.format(name, url, e))
                    return False
        try:
            extractloc = join(tmpdir, 'extracted')
            mkdir(extractloc, exist_ok=True)
            unpack(archiveloc, extractloc)

            extracted_dir = next(ls(extractloc, only_dirs=True, full_paths=True)) # find out what the extracted directory is called. There will be only 1 extracted directory.
            rm(location, ignore_errors=True)
            mkdir(location)
            for x in ls(extracted_dir, full_paths=True): # Move every file and directory to the final location.
                mv(x, location)
            return True
        except Exception as e:
            printe('Could not extract {} zip file correctly, url={}. {}'.format(name, url, e))
            return False


def install_prometheus_node_exporter(location, node_exporter_url, force_reinstall, silent, retries):
    location = os.path.expanduser(location)
    if (not force_reinstall) and isfile(join(location, 'node_exporter')) and isfile('/usr/bin/node_exporter') and isfile('/etc/systemd/system/node_exporter.service'):
        prints('Acceptable node exporter installation detected.')
        return True
    rm(location, ignore_errors=True)
    mkdir(location)
    if (not isfile(location, 'node_exporter')) and not _download_url(location, node_exporter_url, name='Prometheus node exporter', silent=silent, retries=retries):
        return False
    if subprocess.call('sudo cp {} /usr/bin'.format(join(location, 'node_exporter')), shell=True) != 0:
        printe('Could not copy {} to /usr/bin. Location exists: {}'.format(join(location, 'node_exporter'), isfile(location, 'node_exporter')))
        import socket
        print(str(socket.gethostname()))
        printe('cmd={}'.format('sudo cp {} /usr/bin'.format(join(location, 'node_exporter'))))
        return False
    cmd = """sudo python3 -c "
with open('/etc/systemd/system/node_exporter.service', 'w') as f:
    f.write('''
[Unit]
Description=Node Exporter
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/node_exporter

[Install]
WantedBy=multi-user.target
''')
exit(0)
"
"""
    if subprocess.call(cmd, shell=True) != 0:
        printe('Could not write systemd config.')
        return False
    if subprocess.call('sudo systemctl daemon-reload', shell=True) != 0:
        printe('Could not reload daemons.')
        return False
    return True


def install_prometheus_admin(location, node_admin_url, force_reinstall, silent, retries):
    location = os.path.expanduser(location)
    if (not force_reinstall) and isfile(join(location, 'prometheus')) and isfile('/usr/bin/prometheus') and isfile('/etc/systemd/system/prometheus.service'):
        prints('Acceptable admin installation detected.')
        return True
    rm(location, ignore_errors=True)
    mkdir(location)

    if (not isfile(location, 'prometheus')) and not _download_url(location, node_admin_url, name='Prometheus admin url', silent=silent, retries=retries):
        return False
    if subprocess.call('sudo cp {} /usr/bin'.format(join(location, 'prometheus')), shell=True) != 0:
        printe('Could not copy {} to /usr/bin'.format(join(location, 'prometheus')))
        return False
    cmd = """sudo python3 -c "
with open('/etc/systemd/system/prometheus.service', 'w') as f:
    f.write('''
[Unit]
Description=Prometheus
After=network.target
 
[Service]
Type=simple
ExecStart=/usr/bin/prometheus --config.file={}
 
[Install]
WantedBy=multi-user.target
''')
exit(0)
"
""".format(join(location, 'config.yml'))
    if subprocess.call(cmd, shell=True) != 0:
        printe('Could not write admin systemd config.')
        return False
    if subprocess.call('sudo systemctl daemon-reload', shell=True) != 0:
        printe('Could not reload daemons.')
        return False
    return True