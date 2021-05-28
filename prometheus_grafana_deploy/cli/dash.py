import prometheus_grafana_deploy.cli.util as _cli_util
import prometheus_grafana_deploy.internal.defaults.dash as defaults
import prometheus_grafana_deploy.internal.util.location as loc
from prometheus_grafana_deploy.internal.util.printer import *

from prometheus_grafana_deploy.dash import dash as _dash


'''CLI module to generate dashboards for Grafana.'''

def subparser(subparsers):
    '''Register subparser modules'''
    dashparser = subparsers.add_parser('dash', help='Generate dashboard JSON files to visualize data.')
    dashparser.add_argument('generator_names', metavar='names', nargs='+', type=str, help='Generator names to run. All must be available in {}'.format(loc.generators_dir()))
    dashparser.add_argument('-o', '--outputs', metavar='paths', nargs='+', default=[defaults.generated_dir()], type=str, help='Generator output path. If 1 generator is specified, path can point to a filename. Otherwise, a directory will be created, and default generator names will be used.')
    # dashparser.add_argument('--admin', metavar='id', dest='admin_id', type=int, default=None, help='ID of the node of the Prometheus admin node.')
    # dashparser.add_argument('--grafana-port', metavar='number', type=int, default=defaults.grafana_port(), help='Port to use for Grafana.')
    # dashparser.add_argument('--grafana-image', metavar='image', dest='grafana_image', type=str, default=install_defaults.grafana_image(), help='Grafana docker image to use (default={}).'.format(install_defaults.grafana_image()))
    return [dashparser]

def deploy_args_set(args):
    '''Indicates whether we will handle command parse output in this module.
    `deploy()` function will be called if set.

    Returns:
        `True` if we found arguments used by this subsubparser, `False` otherwise.'''
    return args.command == 'dash'

def deploy(parsers, args):
    reservation = _cli_util.read_reservation_cli()
    return _dash(reservation, generator_names=args.generator_names, output_names=args.outputs) if reservation else False