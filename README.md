Python utility to setup K3s cluster on number of devices Raspberry PIs and other devices. It connects to the devices over SSH and performs necesary installation. Along the K3s there is also samba package installed (but not configured) so it can be used in the cluster for some common memory location.

Cluster architecture is determined in JSON file provided to the script as an input parameter.
The layout of JSON file should be as follows:

```json
{
    "k3s_version": "v1.24.6+k3s1",
    "machines": [
        {
            "username": "laptop-vm",
            "node_name": "controler",
            "ip": "192.168.0.74",
            "is_controller": 1,
            "phases": [2, 3, 4]
        },
        {
            "username": "rpi",
            "node_name": "agent0",
            "ip": "192.168.0.75",
            "is_controller": 0,
            "phases": [1, 2, 3, 4]
        },
        ...
        {
            "username": "rpi",
            "node_name": "agentN",
            "ip": "192.168.0.100",
            "is_controller": 0,
            "phases": [1, 2, 3, 4]
        }
    ] 
}
```

Required parameters are:
k3s_version - version of the K3s to be installed on nodes.
machines - list of the machines to setup. Each alement of the list must contain of:
    - username - system username to login with over SSH
    - node_name - descriptive name of the node in the cluster
    - ip - node IP
    - is_controller - 0 or 1 to mark the controller node
    - phases - list of steps 1-4 to perform, see details in further section

# Notes to the input JSON file:
1. The controller node should be listed as the first one so its key is known for other nodes.
2. There should be no more than one controller in the JSON. Otherwise further controllers
will be used and the tool will end up creating more clusters depending on the order in the file.

# Devices Setup
The script can be run against any Linux/Ubuntu/Raspbain OS machines combination. The tool installs required packages and tools for K3s setup. Tested configuration contained 5 RPis with Ubuntu OS or Ubuntu VM hosted on Windows + single RPi with Ubunut OS.
It is recommended to run script against freshly installed OS images, so no previously installed tools interfere with the K3s configuration process.
The tool assumes user password (the one that you type while connecting over SSH to your machines) is the same on all the machines. Feel free to change it after the setup is done.

# Phases executed for K3s installation:
Each of the following paragraphs is considered a **phase** in the setup process that can be run or not depending on the configuration described in JSON file.
First phase is extracted because it is specific to non-Raspbian OS installed on a RPi machine that requires a reboot and additional handling of reconnecting to the Raspberry. Other ones are abstracted in a way that some components can be removed (like K3s itself) and recreated using the tool.

## Phase 0:
Prepare SD cards with operating system flashed for Raspberry Pis or any other machines. 

## Phase 1: OS preparation phase
In the project, it is assumed that each machine will have Ubuntu OS installed running on Raspberry Pi 4. It means that there must be installed kernel module specific for it called *linux-modules-extra-raspi*. Phase 1 consist of installation of given module and other packages required to install K3s later on.
Note: this phase should be skipped in other architectures. In that case, **curl** must be installed manually on given machine as it is necessary for K3s download and installation.

## Phase 2: K3s download and installation
In this phase, K3s is downoladed and installed on each device with given role in a cluster. The script automates any exchange of values required for nodes to connect to controller and cluster.

## Phase 3: Copy over aliases file and install samba
This phase copies file with aliases I like and adds sourcing them to .bashrc file so they are present in terminal whenever user connects. Also samba is installed in this phase but needs to be configured manually after the process is complete.

## Phase 4: Install helm on controller node and send deployment files
In this phase, deployment files present in repository are sent over to controller node. Also Kubernetes package manager **helm** is installed on controller node in this phase. Since running this phase doesn't make much sense for worker nodes, this will be ignored for them. If you really want to make this happen, it needs to be done manually.

You can rule out any of these phases by not marking them to run in JSON file in field machines.phases. To run only K3s installation (2) and sending deployment files (4) the field should look like this:
"phases": [2, 4]  

# Running the tool:
Class that takes care of whole process needs two parameters to be passed:
1. JSON file describing your architecture
2. SSH password - so it's never kept on this repository

There are two ways to run the installation:
1. In your command line run main.py script:
python main.py <your_cluster_rachitecture.json> <ssh_password>

2. In python session, import the module and run it with input as arguments:
>>> from K3sConfiguration import k3s_configurator
>>> configurator = k3s_configurator.K3sRpiConfigurator('cluster.json', 'password')
>>> configurator.configure_nodes()
