import prometheus_grafana_deploy.cli.util as _cli_util
import prometheus_grafana_deploy.internal.defaults.dash as defaults
import prometheus_grafana_deploy.internal.util.location as loc
from prometheus_grafana_deploy.internal.util.printer import *

from prometheus_grafana_deploy.dash import dash_cli as _dash_cli


'''CLI module to generate dashboards for Grafana.'''

def subparser(subparsers):
    '''Register subparser modules'''
    dashparser = subparsers.add_parser('dash', help='Generate dashboard JSON files to visualize data.')
    dashparser.add_argument('generator_name', metavar='name', type=str, help='Generator plugin name to execute. Must be available in: {}'.format(loc.generators_dir()))
    dashparser.add_argument('-o', '--output', metavar='path', default=defaults.generated_dir(), type=str, help='Generator output path. Path can point to a filename. Otherwise, a directory will be created, and a default generator name will be used.')
    dashparser.add_argument('args', metavar='args', nargs='*', help='Arguments for the plugin. Use "grafana-monitor <plugin_name> -- -h" to see possible arguments.')
    return [dashparser]

def deploy_args_set(args):
    '''Indicates whether we will handle command parse output in this module.
    `deploy()` function will be called if set.

    Returns:
        `True` if we found arguments used by this subsubparser, `False` otherwise.'''
    return args.command == 'dash'

def deploy(parsers, args):
    return _dash_cli(args.generator_name, args.args, output=args.output)