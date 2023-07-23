import time
import configparser
from GA.utils.traffic_control import *
from GA.utils.network_interfaces import *
from GA.utils.virsh import *

config_dir = '../config'


def limit_vm_bandwidth_weighted(vm_names, interfaces, total_bandwidth, payments, initialized_vms):
    total_payment = sum(payments[vm_name] for vm_name in vm_names)
    for vm_name in vm_names:
        if vm_name not in initialized_vms:
            tc_init(vm_name, interfaces[vm_name])
            initialized_vms.add(vm_name)

        bw_limit_vm = (payments[vm_name] / total_payment) * total_bandwidth
        bw_limit = f"{bw_limit_vm}gbits"
        tc_limit_bandwidth(vm_name, interfaces[vm_name], bw_limit)


def main():
    config = configparser.ConfigParser()
    config.read(f'{config_dir}/total_bandwidth.ini')
    total_bandwidth = int(config['DEFAULT']['total_bandwidth'])

    payment_config = configparser.ConfigParser()
    payment_config.read(f'{config_dir}payments.ini')
    payments = {vm_name: int(
        payment_config['DEFAULT'][vm_name]) for vm_name in payment_config['DEFAULT']}

    prev_vm_names = set()
    initialized_vms = set()

    while True:
        time.sleep(1)

        vm_names = get_running_vms()
        if vm_names is None:
            print("No running VMs found.")
            continue

        if vm_names != prev_vm_names:
            interfaces = {vm_name: get_last_network_interface(
                vm_name) for vm_name in vm_names}
            new_vms = vm_names - prev_vm_names
            initialized_vms = initialized_vms.intersection(vm_names) | new_vms
            limit_vm_bandwidth_weighted(vm_names, interfaces,
                                        total_bandwidth, payments, initialized_vms)
            prev_vm_names = vm_names


if __name__ == "__main__":
    main()
