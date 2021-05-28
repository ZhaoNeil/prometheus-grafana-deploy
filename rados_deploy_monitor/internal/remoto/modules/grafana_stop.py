import subprocess

def stop_grafana(instance_name, image, port, silent):
    output = subprocess.check_output('sudo docker ps -f "name={0}" --format "{{{{.Names}}}}"'.format(instance_name), **get_subprocess_kwargs(True)).decode('utf-8').strip()
    grafana_running = output == instance_name
    if not grafana_running:
        prints('No running Grafana instance found.')
        return True
    if subprocess.call('sudo docker container {}'.format(instance_name), **get_subprocess_kwargs(silent)) != 0:
        printe('Could not stop Grafana.')
        return False
    return True