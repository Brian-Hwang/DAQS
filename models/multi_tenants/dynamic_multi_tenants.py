import time
from utils.traffic_control import *
from utils.network_interfaces import *
from utils.virsh import *


def limit_vm_bandwidth_dynamically(vm_names, interface, bw_limit):
    first_execution = {vm_name: True for vm_name in vm_names}
    prev_tx_Gbit = {vm_name: check_tc_Gbit(
        vm_name, interface) for vm_name in vm_names}

    # Check VM Status every 1 second
    while True:
        time.sleep(1)  # Wait for 1 second

        curr_tx_Gbit = {vm_name: check_tc_Gbit(
            vm_name, interface) for vm_name in vm_names}
        total_tx_Gbit = sum(curr_tx_Gbit.values())

        for vm_name in vm_names:
            diff_tx_Gbit = curr_tx_Gbit[vm_name] - prev_tx_Gbit[vm_name]
            prev_tx_Gbit[vm_name] = curr_tx_Gbit[vm_name]

            if first_execution[vm_name]:
                tc_init(vm_name, interface)
                tc_limit_bandwidth(vm_name, interface, bw_limit)
                first_execution[vm_name] = False

            elif total_tx_Gbit > 36 and diff_tx_Gbit > 20:
                tc_limit_bandwidth(vm_name, interface, bw_limit)


vm_names = get_running_vms()
bw_limit = "20Gbit"

# Get the last interface for each VM
interfaces = {vm_name: last_network_interface(vm_name) for vm_name in vm_names}

for vm_name, interface in interfaces.items():
    limit_vm_bandwidth_dynamically(vm_name, interface, bw_limit)
