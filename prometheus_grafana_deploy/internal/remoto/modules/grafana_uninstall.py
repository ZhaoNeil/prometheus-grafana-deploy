import subprocess

def uninstall_grafana(image, grafana_name, silent):
    has_docker = subprocess.call('which docker', **get_subprocess_kwargs(silent)) == 0
    if not has_docker:
        printw('Docker no longer available. Skipping uninstallation of Grafana.')
        return True
    stop_grafana(grafana_name, True)

    subprocess.call('sudo docker container rm {}'.format(grafana_name), **get_subprocess_kwargs(True))

    if image:
        has_grafana_image = subprocess.call('sudo docker image inspect {}'.format(image), **get_subprocess_kwargs(True)) == 0
        if has_grafana_image:
            subprocess.call('sudo docker image rm {}'.format(image), **get_subprocess_kwargs(silent))
    return True