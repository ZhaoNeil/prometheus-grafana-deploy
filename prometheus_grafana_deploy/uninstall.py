import concurrent.futures
import hashlib
import subprocess
import tempfile

import prometheus_grafana_deploy.internal.defaults.uninstall as defaults
import prometheus_grafana_deploy.internal.defaults.install as install_defaults
import prometheus_grafana_deploy.internal.defaults.start as start_defaults
from prometheus_grafana_deploy.internal.remoto.modulegenerator import ModuleGenerator
from prometheus_grafana_deploy.internal.remoto.ssh_wrapper import get_wrappers, close_wrappers
import prometheus_grafana_deploy.internal.util.fs as fs
import prometheus_grafana_deploy.internal.util.importer as importer
import prometheus_grafana_deploy.internal.util.location as loc
from prometheus_grafana_deploy.internal.util.printer import *


def _uninstall_prometheus_node_exporter(connection, module, install_dir, silent=False, retries=defaults.retries()):
    remote_module = connection.import_module(module)
    if not remote_module.uninstall_prometheus_node_exporter(loc.prometheus_exporterdir(install_dir), silent, retries):
        printe('Could not uninstall prometheus node exporter.')
        return False
    return True


def _uninstall_prometheus_admin(connection, module, install_dir, silent=False, retries=defaults.retries()):
    remote_module = connection.import_module(module)
    if not remote_module.uninstall_prometheus_admin(loc.prometheus_admindir(install_dir), silent, retries):
        printe('Could not uninstall Prometheus admin from some node(s).')
        return False
    return True


def _uninstall_grafana(connection, module, image=install_defaults.grafana_image(), grafana_name=start_defaults.grafana_name(), silent=False):
    remote_module = connection.import_module(module)
    if not remote_module.uninstall_grafana(image, grafana_name, silent):
        printe('Could not uninstall Grafana.')
        return False
    return True


def _generate_module_uninstall(silent=False):
    '''Generates Prometheus-install module from available sources.'''
    generation_loc = fs.join(fs.dirname(fs.abspath(__file__)), 'internal', 'remoto', 'modules', 'generated', 'all_uninstall.py')
    files = [
        fs.join(fs.dirname(fs.abspath(__file__)), 'internal', 'util', 'printer.py'),
        fs.join(fs.dirname(fs.abspath(__file__)), 'internal', 'remoto', 'modules', 'printer.py'),
        fs.join(fs.dirname(fs.abspath(__file__)), 'internal', 'remoto', 'modules', 'util.py'),
        fs.join(fs.dirname(fs.abspath(__file__)), 'internal', 'remoto', 'modules', 'prometheus_stop.py'),
        fs.join(fs.dirname(fs.abspath(__file__)), 'internal', 'remoto', 'modules', 'prometheus_uninstall.py'),
        fs.join(fs.dirname(fs.abspath(__file__)), 'internal', 'remoto', 'modules', 'grafana_stop.py'),
        fs.join(fs.dirname(fs.abspath(__file__)), 'internal', 'remoto', 'modules', 'grafana_uninstall.py'),
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


def uninstall(reservation, install_dir=install_defaults.install_dir(), key_path=None, admin_id=None, connectionwrappers=None, grafana_image=install_defaults.grafana_image(), grafana_name=start_defaults.grafana_name(), silent=False, retries=defaults.retries()):
    '''Uninstalls Prometheus+Grafana from a remote cluster.
    Args:
        reservation (`metareserve.Reservation`): Reservation object with all nodes to install Prometheus on.
        install_dir (optional str): Location on remote host to store Prometheus in.
        key_path (optional str): Path to SSH key, which we use to connect to nodes. If `None`, we do not authenticate using an IdentityFile.
        admin_id (optional int): Node id that must become the admin. If `None`, the node with lowest public ip value (string comparison) will be picked.
        connectionwrappers (optional dict(metareserve.Node, RemotoSSHWrapper)): If set, uses given connections, instead of building new ones.
        grafana_image (optonal str): If set, removes Grafana Docker image name.
        grafana_name (optional str): Name of the previously spawned container.
        silent (optional bool): If set, does not print so much info.
        retries (optional int): Number of retries before we error.

    Returns:
        `True, admin_node_id` on success, `False, None` otherwise.'''
    admin_picked, _ = _pick_admin(reservation, admin=admin_id)
    printc('Picked admin node: {}'.format(admin_picked), Color.CAN)
    
    local_connections = connectionwrappers == None
    if local_connections:
        ssh_kwargs = {'IdentitiesOnly': 'yes', 'User': admin_picked.extra_info['user'], 'StrictHostKeyChecking': 'no'}
        if key_path:
            ssh_kwargs['IdentityFile'] = key_path
        else:
            printw('Connections have no assigned ssh key. Prepare to fill in your password often.')
        connectionwrappers = get_wrappers(reservation.nodes, lambda node: node.ip_public, ssh_params=ssh_kwargs, silent=silent)
    if not all(x.open for x in connectionwrappers.values()):
        if local_connections:
            close_wrappers(connectionwrappers)
        printe('Failed to create at least one connection.')
        return False, None

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(reservation)+2) as executor:
        uninstall_module = _generate_module_uninstall()
        futures_uninstall = [executor.submit(_uninstall_prometheus_node_exporter, wrapper.connection, uninstall_module, install_dir, silent=silent, retries=retries) for wrapper in connectionwrappers.values()]

        futures_uninstall.append(executor.submit(_uninstall_prometheus_admin, connectionwrappers[admin_picked].connection, uninstall_module, install_dir, silent=silent, retries=retries))
        futures_uninstall.append(executor.submit(_uninstall_grafana, connectionwrappers[admin_picked].connection, uninstall_module, image=grafana_image, grafana_name=grafana_name, silent=silent))
        if not all(x.result() for x in futures_uninstall):
            if local_connections:
                close_wrappers(connectionwrappers)
            return False, None
    prints('Prometheus+Grafana uninstalled from all nodes.')
    if local_connections:
        close_wrappers(connectionwrappers)
    return True, admin_picked.node_id