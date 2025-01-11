import json
from .k3s_controller_factory import K3sControllerFactory


class K3sRpiConfigurator:
    def __init__(self, json_file, password):
        # Keep the nodes in a list:
        self.nodes = []
        self.controller_token = None
        self.controller_ip = None

        # Get the configurations from the JSON file:
        with open(json_file) as jf:
            json_data = json.load(jf)
            self.k3s_install_version = json_data['k3s_version']

            for rpi_config in json_data['machines']:
                k3s = K3sControllerFactory(rpi_config, password).get_node()
                self.nodes.append(k3s)

    def configure_nodes(self):
        print("Begin configuration of the nodes:")
        for node in self.nodes:
            if node.did_connection_fail():
                print(f"Skipping node {node.ip} due to failed SSH connection.")
                continue

            print(f"\tStarting configuration of node {node.node_name}:{node.ip}")
            # Phase 1: OS preparation phase - installing required modules
            #          and applying settings.
            if node.check_if_running_current_phase(1):
                node.install_required_modules()

            # Phase 2: K3s configuration file and download
            if node.check_if_running_current_phase(2):
                node.prepare_k3s_config_file()
                node.install_k3s(self.k3s_install_version, self.controller_ip,
                                    self.controller_token)
                node.write_final_k3s_config_file()
                # Get the token and IP from the controller to pass it to the nodes:
                if self.controller_token is None:
                    self.controller_token = node.get_controller_token(None)
                    self.controller_ip = node.get_controller_ip()
            # Phase 3: Copying aliases file to nodes and install samba: 
            if node.check_if_running_current_phase(3):
                node.send_and_source_aliases()
                node.install_and_setup_samba()
                node.helm_install()

            # Phase 4: Send deployment files
            if node.check_if_running_current_phase(4):
                node.send_deployment_files()

            print(f"\tFinished configuration of node {node.node_name}:{node.ip}")

        # Phase 5: Run deployments once cluster is ready
        if self.nodes[0].check_if_running_current_phase(5):
            self.nodes[0].run_deployments()
        print("Finished configuration of all the nodes from the JSON file that were connected.")


    def transfer_nodes(self):
        new_token = self.nodes[0].get_controller_token()

        for node in self.nodes[1:-1]:
            node.ssh.sudo_command("unagent")
            node.install_k3s(self.k3s_install_version, self.nodes[0].ip, new_token)
            self.nodes[-1].ssh.command(f'kubectl delete node {node.node_name}')
