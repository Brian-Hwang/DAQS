import time
import datetime
import utils.traffic_control as tc
import utils.guest_utils as guest
import utils.host_utils as host
import utils.read_config as cfg

MONITOR_PERIOD = datetime.timedelta(milliseconds=100)
IGNORE_BW_THRESHOLD_GBPS = 1
MARGINAL_RATE = 1
MARGINAL_OFFSET = 1
STEP_GBPS = 0.2
TOLERANT_USAGE_RATE = 1.0 - (((2**30)/(10**9))-1)*2


def get_current_time_and_gbits(vm_name, iface, prev_time, prev_bytes):
    current_time = datetime.datetime.now()
    current_gbits = guest.check_tx_gbits(vm_name, iface)
    if prev_bytes == -1:
        speed = -1
    else:
        speed = guest.get_tx_speed_gbps(
            prev_time, prev_bytes, current_time, current_gbits)
    return current_time, current_gbits, speed


def get_fasten_speed(current_regulated_speed, step):
    target_speed = current_regulated_speed - step
    if target_speed <= 1:
        target_speed = 1
    return target_speed


def get_loosen_speed(current_regulated_speed, step, host_bandwidth):
    target_speed = current_regulated_speed + step
    if target_speed > host_bandwidth:
        target_speed = host_bandwidth
    return target_speed


def calculate_regulated_speed(current_guaranteed_speed, total_guaranteed_speed, host_bandwidth, current_total_speed, regulated_speed):
    if current_guaranteed_speed < IGNORE_BW_THRESHOLD_GBPS:
        regulated_speed = -1
    elif current_guaranteed_speed < total_guaranteed_speed:
        if regulated_speed == -1:
            regulated_speed = host_bandwidth * TOLERANT_USAGE_RATE - total_guaranteed_speed
        else:
            if host_bandwidth * TOLERANT_USAGE_RATE <= current_total_speed:
                regulated_speed = get_fasten_speed(regulated_speed, STEP_GBPS)
            elif host_bandwidth * TOLERANT_USAGE_RATE > current_total_speed + STEP_GBPS:
                regulated_speed = get_loosen_speed(
                    regulated_speed, STEP_GBPS, host_bandwidth)
    elif current_guaranteed_speed > total_guaranteed_speed * MARGINAL_RATE + MARGINAL_OFFSET:
        if current_total_speed - current_guaranteed_speed > IGNORE_BW_THRESHOLD_GBPS:
            regulated_speed = get_loosen_speed(
                regulated_speed, STEP_GBPS, host_bandwidth)
    return regulated_speed


def apply_traffic_control(vm, interfaces, guaranteed_vms, regulated_speed, host_bandwidth):
    if vm in guaranteed_vms.keys():
        return
    if regulated_speed == -1 or regulated_speed >= host_bandwidth:
        tc.delete_queue_discipline(vm, interfaces[vm])
    elif regulated_speed > 0:
        tc.set_bandwidth_limit_mbps(
            vm, interfaces[vm], regulated_speed * (2.0**10))


def limit_vm_bandwidth_minimum_guarantee(running_vms, interfaces, host_bandwidth, guaranteed_vms, initialized_vms, regulated_speed, prev_times, prev_bytes):
    if running_vms is None:
        return initialized_vms, regulated_speed

    total_guaranteed_speed = 0
    for guaranteed_vm, guaranteed_speed in guaranteed_vms.items():
        if guaranteed_vm in running_vms:
            total_guaranteed_speed += guaranteed_speed

    current_total_guaranteed_speed = 0
    current_total_speed = 0
    for vm in running_vms:
        if vm not in prev_times:
            prev_times[vm] = datetime.datetime.now()
            prev_bytes[vm] = guest.check_tx_bytes(vm, interfaces[vm])
        else:
            prev_times[vm], prev_bytes[vm], speed = get_current_time_and_gbits(
                vm, interfaces[vm], prev_times[vm], prev_bytes[vm])
            if vm in guaranteed_vms.keys():
                current_total_guaranteed_speed += speed
                current_total_speed += speed
            else:
                current_total_speed += speed

    regulated_speed = calculate_regulated_speed(
        current_total_guaranteed_speed, total_guaranteed_speed, host_bandwidth, current_total_speed, regulated_speed)

    # print(f"VMs: {running_vms}, GVM: {guaranteed_vms} \n" +
    #      f"Total Goal guaranteed speed: {total_guaranteed_speed}, Regulated speed : {regulated_speed}, \n" +
    #      f"Guaranteed speed: {current_total_guaranteed_speed}, Total speed: {current_total_speed}")

    for vm in running_vms:
        apply_traffic_control(vm, interfaces, guaranteed_vms,
                              regulated_speed, host_bandwidth)

    return initialized_vms, regulated_speed


def minimum_guarantee_vm_bandwidth():
    host_interface = cfg.read_host_interface()
    host_bandwidth = host.get_bandwidth(host_interface)
    guaranteed_vms = cfg.read_guaranteed_vms()
    initialized_vms = set()
    regulated_speed = -1
    prev_times = {}
    prev_bytes = {}

    # print(f"Tolerant rate: {TOLERANT_USAGE_RATE}")

    while True:
        start_time = time.perf_counter()
        running_vms = host.get_running_vms()
        if running_vms is None:
            continue

        if running_vms != initialized_vms:
            interfaces = {}
            for vm_name in running_vms:
                while True:
                    try:
                        interfaces[vm_name] = guest.get_last_network_interface(
                            vm_name)
                        break
                    except TypeError:
                        print(f"VM {vm_name} is not fully ready. Waiting...")
            initialized_vms = running_vms

        initialized_vms, regulated_speed = limit_vm_bandwidth_minimum_guarantee(
            running_vms, interfaces, host_bandwidth, guaranteed_vms, initialized_vms, regulated_speed, prev_times, prev_bytes)
        elapsed_time = time.perf_counter() - start_time
        sleep_time = max(0, MONITOR_PERIOD.total_seconds() - elapsed_time)
        # print(f"Elapsed time: {elapsed_time}, sleep {sleep_time} seconds.")
        time.sleep(sleep_time)


if __name__ == "__main__":
    minimum_guarantee_vm_bandwidth()
