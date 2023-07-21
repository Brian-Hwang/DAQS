import time
from utils.traffic_control import *
from utils.network_interfaces import *


def limit_vm_bandwidth_dynamically(vm_name, interface, bw_limit):
    first_execution = True
    prev_tx_Gbit = check_tc_Gbit(vm_name, interface)

    # Check VM Status every 1 second
    while True:
        time.sleep(1)  # Wait for 1 second

        curr_tx_Gbit = check_tc_Gbit(vm_name, interface)
        diff_tx_Gbit = curr_tx_Gbit - prev_tx_Gbit
        prev_tx_Gbit = curr_tx_Gbit

        if first_execution:
            tc_init(vm_name, interface)
            tc_limit_bandwidth(vm_name, interface, bw_limit)
            first_execution = False

        elif diff_tx_Gbit > 20:
            tc_limit_bandwidth


vm_name = "ubuntu_20.04-clone2"
bw_limit = "20Gbit"

# Get the last interface
interface = last_network_interface(vm_name)

limit_vm_bandwidth_dynamically(vm_name, interface, bw_limit)
