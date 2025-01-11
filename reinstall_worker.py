import sys
from K3sConfiguration import k3s_configurator

if len(sys.argv) < 3:
    print("Run as: main.py config-file rpi-password")
    sys.exit(1)

configurator = k3s_configurator.K3sRpiConfigurator(sys.argv[1], sys.argv[2])
token = configurator.nodes[0].get_controller_token(None)
version = configurator.k3s_install_version

for node in configurator.nodes[1:]:
    if node.reinstall:
        node.ssh.sudo_command("unagent")
        node.install_k3s(version, configurator.nodes[0].ip, token)
