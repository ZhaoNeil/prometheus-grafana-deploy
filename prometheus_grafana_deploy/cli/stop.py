import prometheus_grafana_deploy.cli.util as _cli_util
from prometheus_grafana_deploy.stop import stop as _stop


'''CLI module to stop a running Prometheus cluster.'''

def subparser(subparsers):
    '''Register subparser modules'''
    stopparser = subparsers.add_parser('stop', help='Stop Prometheus on a cluster.')
    stopparser.add_argument('--admin', metavar='id', dest='admin_id', type=int, default=None, help='ID of the Prometheus admin node.')
    stopparser.add_argument('--silent', help='If set, less output is shown.', action='store_true')
    return [stopparser]


def deploy_args_set(args):
    '''Indicates whether we will handle command parse output in this module.
    `deploy()` function will be called if set.

    Returns:
        `True` if we found arguments used by this subsubparser, `False` otherwise.'''
    return args.command == 'stop'


def deploy(parsers, args):
    reservation = _cli_util.read_reservation_cli()
    return _stop(reservation, args.install_dir, args.key_path, args.admin_id, silent=args.silent) if reservation else False