import time
from utils.traffic_control import *
from GA_VM_QOS.utils.guest_utils import *


def limit_vm_bandwidth_dynamically(vm_name, interface, bw_limit):
    first_execution = True
    prev_tx_gbits = check_tx_gbits(vm_name, interface)

    # Check VM Status every 1 second
    while True:
        time.sleep(1)  # Wait for 1 second

        curr_tx_gbits = check_tx_gbits(vm_name, interface)
        diff_tx_gbits = curr_tx_gbits - prev_tx_gbits
        prev_tx_gbits = curr_tx_gbits

        if first_execution:
            init(vm_name, interface)
            set_bandwidth_limit(vm_name, interface, bw_limit)
            first_execution = False

        elif diff_tx_gbits > 20:
            set_bandwidth_limit


def main():
    vm_name = "ubuntu_20.04-clone2"
    bw_limit = 20

    # Get the last interface
    interface = get_last_network_interface(vm_name)

    limit_vm_bandwidth_dynamically(vm_name, interface, bw_limit)


if __name__ == "__main__":
    main()
