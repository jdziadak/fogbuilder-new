import json
import proxmoxer
import sys
import time
import urllib3


def create_and_run_vms(json_data, px):
  node = json_data['node']

  for vm in json_data['controllers']:
    vm_parameters = {
      'newid': vm['id'],
      'name': vm['name']
    }

    # Create VM from K3s template
    px.nodes(node).qemu(json_data['template_id']).clone.create(**vm_parameters)
    px.nodes(node).qemu(vm['id']).status.start.post()
    print(f"VM {vm['name']} with ID {vm['id']} created successfully.")
    time.sleep(5)


def wait_for_vms_running(json_data, px):
  node = json_data['node']

  for vm in json_data['controllers']:
    while px.nodes(node).qemu(vm['id']).status.current.get()['status'] != 'running':
      print("wait")
      time.sleep(5)
    print(f"VM {vm['name']} with ID {vm['id']} is running.")

with open('proxmox-pass') as creds:
  lines = creds.readlines()
  proxmox_pass = lines[0].replace('\r','').replace('\n', '')

# Connect to Proxmox server
with open(sys.argv[1], "r") as px:
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

  json_data = json.load(px)
  password = sys.argv[2]
  px_login = f'{json_data['px_login']}@pam'
  px_host = json_data['px_host']
  proxmox = proxmoxer.ProxmoxAPI(px_host, user=px_login, password=proxmox_pass, verify_ssl=False)

  create_and_run_vms(json_data, proxmox)

  wait_for_vms_running(json_data, proxmox)      
