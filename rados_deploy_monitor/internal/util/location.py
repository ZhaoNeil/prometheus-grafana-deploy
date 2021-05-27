import os

def prometheusdir(install_dir):
    '''Path to Prometheus node exporters installation directory.'''
    return os.path.join(install_dir, 'prometheus')

def prometheus_exporterdir(install_dir):
    return os.path.join(prometheusdir(install_dir), 'exporter')

def prometheus_admindir(install_dir):
    return os.path.join(prometheusdir(install_dir), 'admin')