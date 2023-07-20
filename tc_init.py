import subprocess
import json
import time

def get_last_interface(vm_name):
    cmd = [
        "sudo", "virsh", "qemu-agent-command", vm_name,
        '{"execute": "guest-network-get-interfaces"}', "--pretty"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)

    # Return the name of the last interface
    return data["return"][-1]["name"]

def init_traffic_control(vm_name, interface, bw_limit, command):
    cmd = [
        "virsh", "qemu-agent-command", vm_name,
        '{"execute": "guest-exec", "arguments": { "path": "/bin/bash", "arg": ["-c", "' + command.format(interface=interface, bw_limit=bw_limit) + '"], "capture-output": true }}', "--pretty"
    ]
    subprocess.run(cmd)


# Set your VM name and bandwidth limit
vm_name = "ubuntu20.04-clone2"
bw_limit = "20Gbit"

# Get the last interface
interface = get_last_interface(vm_name)

command = "sudo tc qdisc del dev {interface} root"

init_traffic_control(vm_name, interface, bw_limit, command)
