from utils.traffic_control import *
from utils.network_interfaces import *


def limit_vm_bandwidth_once(vm_name, interface, bw_limit):
    tc_init(vm_name, interface)
    tc_limit_bandwidth(vm_name, interface, bw_limit)


def main():
    # Set VM name and bandwidth limit
    vm_name = "ubuntu20.04-clone2"
    bw_limit = "20Gbit"

    # Get the last interface
    interface = last_network_interface(vm_name)

    tc_limit_bandwidth(vm_name, interface, bw_limit)


if __name__ == "__main__":
    main()
