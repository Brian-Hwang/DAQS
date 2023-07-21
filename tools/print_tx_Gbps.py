import subprocess
import json
import time
from utils.traffic_control import *
from utils.network_interfaces import *


def print_tc_Gbit(vm_name, interface):
    # Get the current transmitted Gbits
    prev_tx_Gbits = check_tc_Gbit(vm_name, interface)
    while True:
        time.sleep(1)  # Wait for 1 second

        curr_tx_Gbits = check_tc_Gbit(vm_name, interface)
        diff_tx_Gbits = curr_tx_Gbits - prev_tx_Gbits
        prev_tx_Gbits = curr_tx_Gbits

        # Print with 6 decimal places
        print(
            f"Data transmitted : {diff_tx_Gbits:.6f} Gbits/s")


vm_name = "ubuntu20.04-clone2"

# Get the last interface
interface = last_network_interface(vm_name)

print_tc_Gbit(vm_name, interface)
