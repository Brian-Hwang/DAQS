import subprocess
import json
import time

# Get Network Interface name from VM (ex: enp6s0)
def get_last_interface(vm_name):
    cmd = [
        "sudo", "virsh", "qemu-agent-command", vm_name, 
        '{"execute": "guest-network-interfaces"}', "--pretty"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)

    # Return the name of the last interface
    return data["return"][-1]["name"]

# Run commands to limit bandwidth
def limit_vm_bandwidth(vm_name, interface, bw_limit, commands):
    for command in commands:
        cmd = [
            "virsh", "qemu-agent-command", vm_name,
            '{"execute": "guest-exec", "arguments": { "path": "/bin/bash", "arg": ["-c", "' + command.format(interface=interface, bw_limit=bw_limit) + '"], "capture-output": true }}', "--pretty"
        ]
        subprocess.run(cmd)

def check_tc_byte(vm_name, interface):
    cmd = [
        "sudo", "virsh", "qemu-agent-command", vm_name, 
        '{"execute": "guest-network-get-interfaces"}', "--pretty"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)

    # Find the interface by name
    for iface in data["return"]:
        if iface["name"] == interface:
            tx_bytes = int(iface["tx-bytes"])
            return tx_bytes
    
    return 0

def limit_vm_bandwidth_dynamically(vm_name, interface, bw_limit, commands):
    first_execution = True
    prev_tx_bytes = check_tc_byte(vm_name, interface)

    #Check VM Status every 1 second
    while True:
        time.sleep(1)  # Wait for 1 second

        curr_tx_bytes = check_tc_byte(vm_name, interface)
        diff_tx_bytes = curr_tx_bytes - prev_tx_bytes
        prev_tx_bytes = curr_tx_bytes

        print("Difference in tx-bytes:", diff_tx_bytes)

        if first_execution:
            limit_vm_bandwidth(vm_name, interface, bw_limit, commands)
            first_execution = False
        elif diff_tx_bytes > 20000:
            limit_vm_bandwidth(vm_name, interface, bw_limit, commands[2:])

# Set VM name and bandwidth limit
vm_name = "ubuntu_20.04-clone2"
bw_limit = "20Gbit"

# Get the last interface
interface = get_last_interface(vm_name)

commands = [
    "sudo tc qdisc del dev {interface} root",
    "sudo tc qdisc add dev {interface} root handle 1: htb default 10",
    "sudo tc class add dev {interface} parent 1: classid 1:1 htb rate {bw_limit}",
    "sudo tc class add dev {interface} parent 1:1 classid 1:10 htb rate {bw_limit}"
]

limit_vm_bandwidth_dynamically(vm_name, interface, bw_limit, commands)
