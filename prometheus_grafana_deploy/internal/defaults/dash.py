import os

import prometheus_grafana_deploy.internal.util.location as loc

def generated_dir():
    return os.path.join(loc.rootdir(), 'dashboards_generated')