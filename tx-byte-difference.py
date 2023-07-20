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
            tx_bytes = iface["statistics"]["tx-bytes"]
            return tx_bytes

    return 0

# Set your VM name
vm_name = "ubuntu20.04-clone2"

# Get the last interface
interface = get_last_interface(vm_name)


# Get the current transmitted bytes
prev_tx_bytes = check_tc_byte(vm_name, interface)
while True:
    time.sleep(1)  # Wait for 1 second

    curr_tx_bytes = check_tc_byte(vm_name, interface)
    diff_tx_bytes = (curr_tx_bytes - prev_tx_bytes) / (2**30) * 8  # Convert bytes to Gbits
    prev_tx_bytes = curr_tx_bytes

    # Print with 6 decimal places
    print(f"Data transmitted in the last second: {diff_tx_bytes:.6f} Gbits")
