# Prometheus-Grafana-deploy
A simple Python3 executable & library to setup Prometheus monitoring on remote clusters.
Also launches a Grafana instance to view resource utilization on.


## Usage
Once this project is installed, a `grafana-monitor` CLI program becomes available.
It can perform several commands:
 1. `grafana-monitor install` allows us to install Prometheus+Grafana on remote nodes.
 2. `grafana-monitor start/stop` allos us to start/stop Prometheus+Grafana on remote nodes.


For more information, optional arguments etc use:
```bash
grafana-monitor -h
```

### Reservation Strings
Each command asks the user to provide the reservation string of the cluster to work with.
When using [metareserve](https://github.com/Sebastiaan-Alvarez-Rodriguez/metareserve) to allocate nodes, such a string will be printed.
It looks something like:
```
id,hostname,ip_local,ip_public,port,extra_info
```
```
0|node0|192.168.1.1|100.101.102.200|22|user=Username
1|node1|192.168.1.2|100.101.102.210|22|user=Username
2|node2|192.168.1.3|100.101.102.207|22|user=Username
3|node3|192.168.1.4|100.101.102.208|22|user=Username
4|node4|192.168.1.5|100.101.102.213|22|user=Username
5|node5|192.168.1.6|100.101.102.211|22|user=Username
6|node6|192.168.1.7|100.101.102.209|22|user=Username
7|node7|192.168.1.8|100.101.102.212|22|user=Username
8|node8|192.168.1.9|100.101.102.254|22|user=Username
9|node9|192.168.1.10|100.101.102.200|22|user=Username
```
The `user` field in the `extra_info` is used to connect to the clusters.


## Credits
This work is based on [this](https://github.com/JayjeetAtGithub/prometheus-on-baremetal) repo by JayjeetAtGithub.