import prometheus_grafana_deploy.internal.defaults.uninstall as defaults
import prometheus_grafana_deploy.internal.defaults.install as install_defaults
import prometheus_grafana_deploy.cli.util as _cli_util
from prometheus_grafana_deploy.uninstall import uninstall as _uninstall


'''CLI module to install Prometheus on a cluster.'''

def subparser(subparsers):
    '''Register subparser modules'''
    uninstallparser = subparsers.add_parser('uninstall', help='Uninstall Prometheus+Grafana from server cluster.')
    uninstallparser.add_argument('--admin', metavar='id', dest='admin_id', type=int, default=None, help='ID of the Prometheus admin node.')
    uninstallparser.add_argument('--grafana-image', metavar='image', dest='grafana_image', type=str, nargs='?', default=None, const=install_defaults.grafana_image(), help='If set, deletes given Grafana docker image. If set without an argument, default={}.'.format(install_defaults.grafana_image()))
    uninstallparser.add_argument('--silent', help='If set, less boot output is shown.', action='store_true')
    uninstallparser.add_argument('--retries', metavar='amount', type=int, default=defaults.retries(), help='Amount of retries to use for risky operations (default={}).'.format(defaults.retries()))
    return [uninstallparser]


def deploy_args_set(args):
    '''Indicates whether we will handle command parse output in this module.
    `deploy()` function will be called if set.

    Returns:
        `True` if we found arguments used by this subsubparser, `False` otherwise.'''
    return args.command == 'uninstall'


def deploy(parsers, args):
    reservation = _cli_util.read_reservation_cli()
    if not reservation:
        return False
    return _uninstall(reservation, args.install_dir, args.key_path, args.admin_id, grafana_image=args.grafana_image, silent=args.silent, retries=args.retries) if reservation else False