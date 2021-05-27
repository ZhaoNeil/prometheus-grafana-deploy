import concurrent.futures
import hashlib
import subprocess
import tempfile

import rados_deploy_monitor.internal.defaults.install as defaults
from rados_deploy_monitor.internal.remoto.modulegenerator import ModuleGenerator
from rados_deploy_monitor.internal.remoto.util import get_ssh_connection as _get_ssh_connection
import rados_deploy_monitor.internal.util.fs as fs
import rados_deploy_monitor.internal.util.importer as importer
import rados_deploy_monitor.internal.util.location as loc
from rados_deploy_monitor.internal.util.printer import *


def _install_prometheus_node_exporter(connection, module, install_dir, node_exporter_url=defaults.node_exporter_url(), force_reinstall=False, silent=False, retries=defaults.retries()):
    remote_module = connection.import_module(module)

    if not remote_module.install_prometheus_node_exporter(loc.prometheus_exporterdir(install_dir), node_exporter_url, force_reinstall, silent, retries):
        printe('Could not install prometheus node exporter.')
        return False
    return True


def _install_prometheus_admin(connection, module, install_dir, prometheus_url=defaults.prometheus_url(), force_reinstall=False, silent=False, retries=defaults.retries()):
    remote_module = connection.import_module(module)
    if not remote_module.install_prometheus_admin(loc.prometheus_admindir(install_dir), prometheus_url, force_reinstall, silent, retries):
        printe('Could not install Prometheus admin on some node(s).')
        return False
    return True


def _generate_module_prometheus_install(silent=False):
    '''Generates Prometheus-install module from available sources.'''
    generation_loc = fs.join(fs.dirname(fs.abspath(__file__)), 'internal', 'remoto', 'modules', 'generated', 'install_prometheus.py')
    files = [
        fs.join(fs.dirname(fs.abspath(__file__)), 'internal', 'util', 'printer.py'),
        fs.join(fs.dirname(fs.abspath(__file__)), 'internal', 'remoto', 'modules', 'printer.py'),
        fs.join(fs.dirname(fs.abspath(__file__)), 'internal', 'remoto', 'env.py'),
        fs.join(fs.dirname(fs.abspath(__file__)), 'internal', 'remoto', 'modules', 'prometheus_install.py'),
        fs.join(fs.dirname(fs.abspath(__file__)), 'internal', 'remoto', 'modules', 'remoto_base.py'),
    ]
    ModuleGenerator().with_modules(fs).with_files(*files).generate(generation_loc, silent)
    return importer.import_full_path(generation_loc)


def _pick_admin(reservation, admin=None):
    '''Picks a Prometheus admin node.
    Args:
        reservation (`metareserve.Reservation`): Reservation object to pick admin from.
        admin (optional int): If set, picks node with given `node_id`. Picks node with lowest public ip value, otherwise.

    Returns:
        admin, list of non-admins.'''
    if len(reservation) == 1:
        return next(reservation.nodes), []

    if admin:
        return reservation.get_node(node_id=admin), [x for x in reservation.nodes if x.node_id != admin]
    else:
        tmp = sorted(reservation.nodes, key=lambda x: x.ip_public)
        return tmp[0], tmp[1:]


def _merge_kwargs(x, y):
    z = x.copy()
    z.update(y)
    return z


def install(reservation, install_dir=defaults.install_dir(), key_path=None, admin_id=None, node_exporter_url=defaults.node_exporter_url(), prometheus_url=defaults.prometheus_url(), force_reinstall=False, silent=False, retries=defaults.retries()):
    '''Installs Prometheus on remote cluster.
    Args:
        reservation (`metareserve.Reservation`): Reservation object with all nodes to install Prometheus on.
        install_dir (optional str): Location on remote host to store Prometheus in.
        key_path (optional str): Path to SSH key, which we use to connect to nodes. If `None`, we do not authenticate using an IdentityFile.
        admin_id (optional int): Node id that must become the admin. If `None`, the node with lowest public ip value (string comparison) will be picked.
        node_exporter_url (optional str): Download URL for Prometheus node exporter.
        prometheus_url (optional str): Download URL for Prometheus.
        force_reinstall (optional bool): If set, we always will re-download and install. Otherwise, we will skip installing if we already find an installation.
        silent (optional bool): If set, does not print so much info.
        retries (optional int): Number of retries before we error.

    Returns:
        `True, admin_node_id` on success, `False, None` otherwise.'''
    admin_picked, _ = _pick_admin(reservation, admin=admin_id)
    printc('Picked admin node: {}'.format(admin_picked), Color.CAN)
        
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(reservation)) as executor:
        ssh_kwargs = {'IdentitiesOnly': 'yes', 'StrictHostKeyChecking': 'no'}
        if key_path:
            ssh_kwargs['IdentityFile'] = key_path
        else:
            printw('Connections have no assigned ssh key. Prepare to fill in your password often.')
        futures_connection = {x: executor.submit(_get_ssh_connection, x.ip_public, silent=silent, ssh_params=_merge_kwargs(ssh_kwargs, {'User': x.extra_info['user']})) for x in reservation.nodes}
        connectionwrappers = {k: v.result() for k,v in futures_connection.items()}
        
        prometheus_install_module = _generate_module_prometheus_install()
        futures_exporter_install = [executor.submit(_install_prometheus_node_exporter, wrapper.connection, prometheus_install_module, install_dir, node_exporter_url=defaults.node_exporter_url(), force_reinstall=force_reinstall, silent=silent, retries=retries) for wrapper in connectionwrappers.values()]
        if not all(x.result() for x in futures_exporter_install):
            return False, None

    if not _install_prometheus_admin(connectionwrappers[admin_picked].connection, prometheus_install_module, install_dir, prometheus_url=defaults.prometheus_url(), force_reinstall=force_reinstall, silent=silent, retries=retries):
        return False, None
    prints('Prometheus installed on all nodes.')
    return True, admin_picked.node_id