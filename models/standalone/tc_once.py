from ..utils.traffic_control import *
from ..utils.network_interfaces import *
from ..utils.virsh import *


def limit_vm_bandwidth_once(vm_name, interface, bw_limit):
    tc_init(vm_name, interface)
    tc_limit_bandwidth(vm_name, interface, bw_limit)


def main():
    # Set VM name and bandwidth limit
    vm_name = get_running_vms()[0]  # Get the first running VM
    bw_limit = "20gbits"

    # Get the last interface
    interface = get_last_network_interface(vm_name)

    tc_limit_bandwidth(vm_name, interface, bw_limit)


if __name__ == "__main__":
    main()
