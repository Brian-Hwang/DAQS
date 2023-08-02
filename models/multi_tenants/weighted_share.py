import time
import utils.traffic_control as tc
import utils.guest_utils as guest
import utils.host_utils as host
import utils.read_config as cfg


def limit_vm_bandwidth_weighted(vm_names, interfaces, total_bandwidth, payments, initialized_vms):
    """
    Function to limit the bandwidth of virtual machines proportionally to their payments.
    vm_names: list of names of the VMs
    interfaces: mapping of VM names to their respective interfaces
    total_bandwidth: total bandwidth available
    payments: mapping of VM names to their respective payments
    initialized_vms: set of VMs that have been initialized
    """
    total_payment = sum(payments[vm_name] for vm_name in vm_names)

    for vm_name in vm_names:
        bw_limit_vm = (payments[vm_name] / total_payment) * total_bandwidth
        print(vm_name, payments[vm_name], bw_limit_vm)

        is_initialized = vm_name in initialized_vms
        tc.set_bandwidth_limit(
            vm_name, interfaces[vm_name], bw_limit_vm, is_initialized)
        initialized_vms.add(vm_name)


def weighted_share_vm_bandwidth():
    """
    Function to manage the bandwidth of VMs.
    It continuously monitors the VMs and adjusts their bandwidth.
    """
    host_interface = cfg.read_host_interface()
    host_bandwidth = host.get_bandwidth(host_interface)

    prev_vm_names = set()
    initialized_vms = set()

    while True:

        payments = cfg.read_payments()
        start_time = time.perf_counter()

        vm_names = host.get_running_vms()
        if vm_names is None:
            continue

        if vm_names != prev_vm_names or not initialized_vms:
            interfaces = {}
            ready_vms = set()

            for vm_name in vm_names:
                while True:
                    try:
                        interfaces[vm_name] = guest.get_last_network_interface(
                            vm_name)
                        ready_vms.add(vm_name)
                        break
                    except TypeError:
                        print(f"VM {vm_name} is not fully ready. Waiting...")
                        time.sleep(1)

            if len(ready_vms) == 1:
                vm_name = next(iter(ready_vms))  # get the only VM
                tc.delete_queue_discipline(vm_name, interfaces[vm_name])
                initialized_vms.discard(vm_name)
            else:
                limit_vm_bandwidth_weighted(
                    ready_vms, interfaces, host_bandwidth, payments, initialized_vms)

            initialized_vms = initialized_vms.intersection(ready_vms)
            prev_vm_names = ready_vms

        elapsed_time = time.perf_counter() - start_time
        sleep_time = max(0, 1 - elapsed_time)
        time.sleep(sleep_time)


if __name__ == "__main__":
    weighted_share_vm_bandwidth()
