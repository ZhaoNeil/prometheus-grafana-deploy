import prometheus_grafana_deploy.internal.defaults.dash as defaults
import prometheus_grafana_deploy.internal.util.fs as fs
import prometheus_grafana_deploy.internal.util.importer as importer
import prometheus_grafana_deploy.internal.util.location as loc
from prometheus_grafana_deploy.internal.util.printer import *


def _load_generator(name):
    module = importer.import_full_path(fs.join(loc.generators_dir(), name))
    return module


def dash(reservation, generator_names, output_names=[defaults.generated_dir()]):
    if len(generator_names) > 1:
        if len(output_names) > 1 and len(output_names) != len(generator_names):
            printe('Must specify either 1 directory output or {0} file outputs for {0} generators.'.format(len(generator_names)))
            return False
        else:
            output_names = [output_names[0] for _ in range(len(generator_names))]
    generators = dict()
    fs.mkdir(defaults.generated_dir(), exist_ok=True)

    for name in generator_names:
        if (not fs.isfile(loc.generators_dir(), name)) and not name.endswith('.py'):
            name = name+'.py'
        if not fs.isfile(loc.generators_dir(), name):
            printe('Generator "{}" not found at: {}'.format(name, fs.join(loc.generators_dir(), name)))
            return False
        generators[name] = _load_generator(name)

    for (name, module), output in zip(generators.items(), output_names):
        print('Generating using generator "{}". Output: {}'.format(name, output))
        if not module.generate(reservation, output):
            fs.mkdir()
            printe('Generator "{}" indicated an error occured.')
            return False
    return True