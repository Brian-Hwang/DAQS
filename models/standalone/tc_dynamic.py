import time
from GA.utils.traffic_control import *
from GA.utils.network_interfaces import *


def limit_vm_bandwidth_dynamically(vm_name, interface, bw_limit):
    first_execution = True
    prev_tx_gbits = check_tx_gbits(vm_name, interface)

    # Check VM Status every 1 second
    while True:
        time.sleep(1)  # Wait for 1 second

        curr_tx_gbits = check_tx_gbits(vm_name, interface)
        diff_tx_gbits = curr_tx_gbits - prev_tx_gbit
        prev_tx_gbits = curr_tx_gbit

        if first_execution:
            tc_init(vm_name, interface)
            tc_limit_bandwidth(vm_name, interface, bw_limit)
            first_execution = False

        elif diff_tx_gbits > 20:
            tc_limit_bandwidth


def main():
    vm_name = "ubuntu_20.04-clone2"
    bw_limit = "20gbits"

    # Get the last interface
    interface = get_last_network_interface(vm_name)

    limit_vm_bandwidth_dynamically(vm_name, interface, bw_limit)


if __name__ == "__main__":
    main()
