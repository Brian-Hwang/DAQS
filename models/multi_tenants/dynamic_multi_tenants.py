import time
from utils.traffic_control import *
from GA_VM_QOS.utils.guest_utils import *
from GA_VM_QOS.utils.host_utils import *


def limit_vm_bandwidth_dynamically(vm_names, interface, bw_limit):
    first_execution = {vm_name: True for vm_name in vm_names}
    prev_tx_gbits = {vm_name: check_tx_gbits(
        vm_name, interface) for vm_name in vm_names}

    # Check VM Status every 1 second
    while True:
        time.sleep(1)  # Wait for 1 second

        curr_tx_gbits = {vm_name: check_tx_gbits(
            vm_name, interface) for vm_name in vm_names}
        total_tx_gbits = sum(curr_tx_gbits.values())

        for vm_name in vm_names:
            diff_tx_gbits = curr_tx_gbits[vm_name] - prev_tx_gbits[vm_name]
            prev_tx_gbits[vm_name] = curr_tx_gbits[vm_name]

            if first_execution[vm_name]:
                init(vm_name, interface)
                set_bandwidth_limit(vm_name, interface, bw_limit)
                first_execution[vm_name] = False

            elif total_tx_gbits > 36 and diff_tx_gbits > 20:
                set_bandwidth_limit(vm_name, interface, bw_limit)


vm_names = get_running_vms()
bw_limit = "20Gbitss"

# Get the last interface for each VM
interfaces = {vm_name: get_last_network_interface(
    vm_name) for vm_name in vm_names}

for vm_name, interface in interfaces.items():
    limit_vm_bandwidth_dynamically(vm_name, interface, bw_limit)
