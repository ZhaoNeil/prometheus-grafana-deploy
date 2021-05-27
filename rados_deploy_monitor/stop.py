import concurrent.futures
import hashlib
import subprocess
import tempfile

import rados_deploy_monitor.internal.defaults.install as install_defaults
from rados_deploy_monitor.internal.remoto.modulegenerator import ModuleGenerator
from rados_deploy_monitor.internal.remoto.util import get_ssh_connection as _get_ssh_connection
import rados_deploy_monitor.internal.util.fs as fs
import rados_deploy_monitor.internal.util.importer as importer
import rados_deploy_monitor.internal.util.location as loc
from rados_deploy_monitor.internal.util.printer import *


def _stop_prometheus_node_exporter(connection, module, install_dir, silent=False):
    remote_module = connection.import_module(module)

    if not remote_module.stop_prometheus_node_exporter(loc.prometheus_exporterdir(install_dir), silent):
        printe('Could not stop prometheus node exporter.')
        return False
    return True


def _stop_prometheus_admin(connection, module, install_dir, silent=False):
    if not remote_module.stop_prometheus_admin(loc.prometheus_admindir(install_dir), silent):
        printe('Could not stop Prometheus admin on some node(s).')
        return False
    return True


def _generate_module_prometheus_stop(silent=False):
    '''Generates Prometheus-stop module from available sources.'''
    generation_loc = fs.join(fs.dirname(fs.abspath(__file__)), 'internal', 'remoto', 'modules', 'generated', 'prometheus_stop.py')
    files = [
        fs.join(fs.dirname(fs.abspath(__file__)), 'internal', 'util', 'printer.py'),
        fs.join(fs.dirname(fs.abspath(__file__)), 'internal', 'remoto', 'modules', 'printer.py'),
        fs.join(fs.dirname(fs.abspath(__file__)), 'internal', 'remoto', 'modules', 'rados_stop.py'),
        fs.join(fs.dirname(fs.abspath(__file__)), 'internal', 'remoto', 'modules', 'remoto_base.py'),
    ]
    ModuleGenerator().with_modules(fs, importer).with_files(*files).generate(generation_loc, silent)
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


def stop(reservation, install_dir=install_defaults.install_dir(), key_path=None, admin_id=None, silent=False):
    '''Stop Prometheus on remote cluster.
    Args:
        reservation (`metareserve.Reservation`): Reservation object with all nodes to stop Prometheus on.
        install_dir (optional str): Location on remote host to store Prometheus in.
        key_path (optional str): Path to SSH key, which we use to connect to nodes. If `None`, we do not authenticate using an IdentityFile.
        admin_id (optional int): Node id of the admin. If `None`, the node with lowest public ip value (string comparison) will be picked.
        silent (optional bool): If set, does not print so much info.

    Returns:
        `True` on success, `False` otherwise.'''
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

        prometheus_stop_module = _generate_module_prometheus_stop()
        futures_stop = [executor.submit(_stop_prometheus_node_exporter, wrapper.connection, prometheus_stop_module, install_dir, silent=silent) for wrapper in connectionwrappers.values()]
        futures_stop.append(executor.submit(_stop_prometheus_admin, connectionwrappers[admin_picked], prometheus_stop_module, install_dir, silent=silent))
        return all(x.result() for x in futures_stop)