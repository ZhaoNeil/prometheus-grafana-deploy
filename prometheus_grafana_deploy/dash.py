import prometheus_grafana_deploy.cli.util as _cli_util
import prometheus_grafana_deploy.internal.defaults.dash as defaults
import prometheus_grafana_deploy.internal.util.fs as fs
import prometheus_grafana_deploy.internal.util.importer as importer
import prometheus_grafana_deploy.internal.util.location as loc
from prometheus_grafana_deploy.internal.util.printer import *

def _load_generator(name):
    module = importer.import_full_path(fs.join(loc.generators_dir(), name))
    return module


def dash_cli(generator_name, args, output=defaults.generated_dir()):
    fs.mkdir(defaults.generated_dir(), exist_ok=True)
    
    if (not fs.isfile(loc.generators_dir(), generator_name)) and not generator_name.endswith('.py'):
        generator_name = generator_name+'.py'
    if not fs.isfile(loc.generators_dir(), generator_name):
        printe('Generator "{}" not found at: {}'.format(generator_name, fs.join(loc.generators_dir(), generator_name)))
        return False
    module = _load_generator(generator_name)

    state_ok, args, kwargs = module.parse(args)
    if not state_ok:
        return False

    reservation = _cli_util.read_reservation_cli()
    if not reservation:
        return False

    print('Generating using generator "{}". Output: {}'.format(generator_name, output))
    if not module.generate(reservation, output, *args, **kwargs):
        printe('Generator "{}" indicated an error occured.')
        return False
    return True


def dash(reservation, generator_name, output=defaults.generated_dir(), *args, **kwargs):
    fs.mkdir(defaults.generated_dir(), exist_ok=True)

    if (not fs.isfile(loc.generators_dir(), generator_name)) and not generator_name.endswith('.py'):
        generator_name = generator_name+'.py'
    if not fs.isfile(loc.generators_dir(), generator_name):
        printe('Generator "{}" not found at: {}'.format(generator_name, fs.join(loc.generators_dir(), generator_name)))
        return False
    module = _load_generator(generator_name)

    print('Generating using generator "{}". Output: {}'.format(generator_name, output))
    if not module.generate(reservation, output, *args, **kwargs):
        printe('Generator "{}" indicated an error occured.')
        return False
    return True