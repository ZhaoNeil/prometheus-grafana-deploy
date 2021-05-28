import subprocess

def install_grafana(image, force_reinstall, silent):
    has_docker = subprocess.call('which docker', **get_subprocess_kwargs(silent)) == 0
    has_grafana = subprocess.call('sudo docker image inspect {}'.format(image), **get_subprocess_kwargs(True)) == 0

    if (not force_reinstall) and has_docker and has_grafana:
        prints('Acceptable Grafana installation detected.')
        return True
    if not has_docker:
        if subprocess.call('sudo apt install docker.io -y', **get_subprocess_kwargs(silent)) != 0:
            printe('Could not install docker.io.')
            return False
    if force_reinstall or not has_grafana:
        if subprocess.call('sudo docker image pull {}'.format(image), **get_subprocess_kwargs(silent)) != 0:
            printe('Could not fetch grafana/grafana image.')
            return False
    return True