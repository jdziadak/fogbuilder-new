import sys
from K3sConfiguration import k3s_configurator

if len(sys.argv) < 3:
    print("Run as: main.py config-file rpi-password")
    sys.exit(1)

configurator = k3s_configurator.K3sRpiConfigurator(sys.argv[1], sys.argv[2])
configurator.transfer_nodes()
