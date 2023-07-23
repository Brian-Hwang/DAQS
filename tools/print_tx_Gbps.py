import time
from GA.utils.traffic_control import *
from GA.utils.network_interfaces import *


def print_tc_gbits(vm_name, interface):
    # Get the current transmitted gbits
    prev_tx_gbits = check_tx_gbits(vm_name, interface)
    while True:
        time.sleep(1)  # Wait for 1 second

        curr_tx_gbits = check_tx_gbits(vm_name, interface)
        diff_tx_gbits = curr_tx_gbits - prev_tx_gbits
        prev_tx_gbits = curr_tx_gbits

        # Print with 6 decimal places
        print(
            f"Data transmitted : {diff_tx_gbits:.6f} gbits/s")


def main():
    vm_name = "ubuntu20.04-clone2"

    # Get the last interface
    interface = get_last_network_interface(vm_name)

    print_tc_gbits(vm_name, interface)


if __name__ == "__main__":
    main()
