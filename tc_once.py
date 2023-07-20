import subprocess
import json

# Get Network Interface name from VM (ex: enp6s0)
def get_last_interface(vm_name):
    cmd = [
        "sudo", "virsh", "qemu-agent-command", vm_name,
        '{"execute": "guest-network-get-interfaces"}', "--pretty"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)

    # Return the name of the last interface
    return data["return"][-1]["name"]

# Run commands to limit bandwidth
def limit_vm_bandwidth(vm_name, interface, bw_limit, commands):
    for command in commands:
        cmd = [
            "sudo", "virsh", "qemu-agent-command", vm_name,
            '{"execute": "guest-exec", "arguments": { "path": "/bin/bash", "arg": ["-c", "' + command.format(interface=interface, bw_limit=bw_limit) + '"], "capture-output": true }}', "--pretty"
        ]
        subprocess.run(cmd)

# Set VM name and bandwidth limit
vm_name = "ubuntu20.04-clone2"
bw_limit = "20Gbit"

# Get the last interface
interface = get_last_interface(vm_name)

commands = [
    "sudo tc qdisc del dev {interface} root",
    "sudo tc qdisc add dev {interface} root handle 1: htb default 10",
    "sudo tc class add dev {interface} parent 1: classid 1:1 htb rate {bw_limit}",
    "sudo tc class add dev {interface} parent 1:1 classid 1:10 htb rate {bw_limit}"
]

limit_vm_bandwidth(vm_name, interface, bw_limit, commands)
