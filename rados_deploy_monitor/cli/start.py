import rados_deploy_monitor.cli.util as _cli_util


import rados_deploy_monitor.internal.defaults.start as defaults
from rados_deploy_monitor.internal.util.printer import *
from rados_deploy_monitor.start import start as _start


'''CLI module to start Prometheus on a cluster.'''

def subparser(subparsers):
    '''Register subparser modules'''
    startparser = subparsers.add_parser('start', help='Start Prometheus on a cluster.')
    startparser.add_argument('--admin', metavar='id', dest='admin_id', type=int, default=None, help='ID of the node of the Prometheus admin node.')
    startparser.add_argument('--port', metavar='number', type=int, default=defaults.prometheus_port(), help='Port to use for Prometheus.')
    startparser.add_argument('--silent', help='If set, less boot output is shown.', action='store_true')
    return [startparser]

def deploy_args_set(args):
    '''Indicates whether we will handle command parse output in this module.
    `deploy()` function will be called if set.

    Returns:
        `True` if we found arguments used by this subsubparser, `False` otherwise.'''
    return args.command == 'start'

def deploy(parsers, args):
    reservation = _cli_util.read_reservation_cli()
    return _start(reservation, args.key_path, args.admin_id, args.port, silent=args.silent) if reservation else False