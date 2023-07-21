import time
import configparser
from utils.traffic_control import *
from utils.network_interfaces import *
from utils.virsh import *


def limit_vm_bandwidth_evenly(vm_names, interfaces, total_bandwidth, initialized_vms):
    bw_limit_per_vm = total_bandwidth / len(vm_names)
    bw_limit = f"{bw_limit_per_vm}Gbit"

    for vm_name in vm_names:
        if vm_name not in initialized_vms:
            tc_init(vm_name, interfaces[vm_name])
            initialized_vms.add(vm_name)

        tc_limit_bandwidth(vm_name, interfaces[vm_name], bw_limit)


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    total_bandwidth = int(config['DEFAULT']['total_bandwidth'])

    prev_vm_names = set()
    initialized_vms = set()

    while True:
        time.sleep(1)

        vm_names = get_running_vms()
        if vm_names is None:
            continue

        if vm_names != prev_vm_names:
            interfaces = {vm_name: last_network_interface(
                vm_name) for vm_name in vm_names}
            new_vms = vm_names - prev_vm_names
            initialized_vms = initialized_vms.intersection(vm_names) | new_vms
            limit_vm_bandwidth_evenly(
                vm_names, interfaces, total_bandwidth, initialized_vms)
            prev_vm_names = vm_names


if __name__ == "__main__":
    main()
