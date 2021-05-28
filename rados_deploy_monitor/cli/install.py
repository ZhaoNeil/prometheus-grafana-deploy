import rados_deploy_monitor.internal.defaults.install as defaults
import rados_deploy_monitor.cli.util as _cli_util
from rados_deploy_monitor.install import install as _install


'''CLI module to install Prometheus on a cluster.'''

def subparser(subparsers):
    '''Register subparser modules'''
    installparser = subparsers.add_parser('install', help='Install Prometheus on server cluster.')
    installparser.add_argument('--admin', metavar='id', dest='admin_id', type=int, default=None, help='ID of the node that will be the Prometheus admin node.')
    installparser.add_argument('--node-exporter-url', metavar='url', dest='node_exporter_url', type=str, default=defaults.node_exporter_url(), help='Prometheus node exporter download URL.')
    installparser.add_argument('--grafana-image', metavar='image', dest='grafana_image', type=str, default=defaults.grafana_image(), help='Grafana docker image to download (default={}).'.format(defaults.grafana_image()))
    installparser.add_argument('--force-reinstall', dest='force_reinstall', help='If set, we always will re-download and install components. Otherwise, we will skip installing if we already have installed components.', action='store_true')
    installparser.add_argument('--silent', help='If set, less boot output is shown.', action='store_true')
    installparser.add_argument('--retries', metavar='amount', type=int, default=defaults.retries(), help='Amount of retries to use for risky operations (default={}).'.format(defaults.retries()))
    return [installparser]


def deploy_args_set(args):
    '''Indicates whether we will handle command parse output in this module.
    `deploy()` function will be called if set.

    Returns:
        `True` if we found arguments used by this subsubparser, `False` otherwise.'''
    return args.command == 'install'


def deploy(parsers, args):
    reservation = _cli_util.read_reservation_cli()
    if not reservation:
        return False
    return _install(reservation, args.install_dir, args.key_path, args.admin_id, node_exporter_url=args.node_exporter_url, grafana_image=args.grafana_image, force_reinstall=args.force_reinstall, silent=args.silent, retries=args.retries) if reservation else False