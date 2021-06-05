# Prometheus-Grafana-deploy
A simple Python3 executable & library to setup Prometheus monitoring on remote clusters.
Also launches a Grafana instance to view resource utilization on.


## Options
Once this project is installed, a `grafana-monitor` CLI program becomes available.
It can perform several commands:
 1. `grafana-monitor install` allows us to install Prometheus+Grafana on remote nodes.
 2. `grafana-monitor start/stop` allos us to start/stop Prometheus+Grafana on remote nodes. It will also print the Grafana main url 

 > **Note**: the *Prometheus admin* is hosted on the same node (default port 9090) as the Grafana server (default port 3000).


For more information, optional arguments etc use:
```bash
grafana-monitor -h
```


## Usage
In general, you want to execute:
```bash
grafana-monitor install
grafana-monitor start
```

The Grafana UI ip is printed after starting.
In the Grafana UI:
 1. go to `Configuration > Data Sources`, and click the `Add data source` button.
 2. Enter the URL as `http://<Prometheus_admin_IP>:<Prometheus_admin_port>`. 
    The IP was printed during the `start` stage.
    If not changed by the user, the portnumber is `9090`.
 3. Finally, we need to make a dashboard.
    Go to `Dashboards > Manage` and click the `Import` button.
    This tool has the ability to generate dashboards. Use the following command to find out more about a generator named `<generator>`:
```bash
grafana-monitor dash <generator> -- -h
```
 4. Generated dashboards will have JSON format, which is just what Grafana requires.
Copy the JSON contents to the JSON import box, and press the corresponding 'Load' button.

That's it. You now should have a functioning dashboard!


### Reservation Strings
Each command asks the user to provide the reservation string of the cluster to work with.
When using [metareserve](https://github.com/Sebastiaan-Alvarez-Rodriguez/metareserve) to allocate nodes, such a string will be printed.
It looks something like:
```
id,hostname,ip_local,ip_public,port,extra_info
```

An example:
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
9|node9|192.168.1.10|100.101.102.222|22|user=Username
```
The `user` field in the `extra_info` is used to connect to the clusters.


## Credits
This work is based on [this](https://github.com/JayjeetAtGithub/prometheus-on-baremetal) repo by JayjeetAtGithub.