import time
import datetime
import utils.traffic_control as tc
import utils.guest_utils as guest
import utils.host_utils as host
import utils.read_config as cfg
import utils.guest_manager as gm


IGNORE_BW_THRESHOLD_GBPS = 1
MARGINAL_RATE = 1.1
MARGINAL_OFFEST = 0
STEP_GBPS = 1


def minimum_guarantee_vm_bandwidth():
    """
    Function to manage the bandwidth of VMs.
    It continuously monitors the VMs and adjusts their bandwidth.
    """
    host_interface = cfg.read_host_interface()
    host_bandwidth = host.get_bandwidth(host_interface)

    vms = {}
    guaranteed_vms = cfg.read_guaranteed_vms()
    regulated_speed = -1

    while True:
        start_time = time.perf_counter()

        running_vms = host.get_running_vms()
        if running_vms is None:
            continue

        for vm in running_vms:
            if vm not in vms:
                vms[vm] = gm.GuestManager(vm)

        vms = {vm: manager for vm, manager in vms.items() if vm in running_vms}

        guaranteed_speed = sum(
            spd for name, spd in guaranteed_vms.items() if name in running_vms)

        current_speed = 0
        total_speed = 0
        for vm in running_vms:
            spd = vms[vm].get_tx_speed_mbps() / (2.0**10)
            if vm in guaranteed_vms:
                current_speed += spd
            total_speed += spd

        if current_speed < IGNORE_BW_THRESHOLD_GBPS:
            regulated_speed = -1
        elif current_speed < guaranteed_speed:
            regulated_speed = max(
                1, regulated_speed - STEP_GBPS) if regulated_speed != -1 else host_bandwidth - guaranteed_speed
        elif current_speed > guaranteed_speed * MARGINAL_RATE + MARGINAL_OFFEST and total_speed - current_speed > IGNORE_BW_THRESHOLD_GBPS:
            regulated_speed = min(
                host_bandwidth - guaranteed_speed, regulated_speed + STEP_GBPS)

        if regulated_speed > 0:
            for vm in running_vms:
                if vm not in guaranteed_vms:
                    tc.set_bandwidth_limit(vm, vms[vm].iface, regulated_speed)
        elif regulated_speed == -1:
            for vm in running_vms:
                tc.delete_queue_discipline(vm, vms[vm].iface)

        elapsed_time = time.perf_counter() - start_time
        sleep_time = max(0, 1 - elapsed_time)
        time.sleep(sleep_time)


if __name__ == "__main__":
    minimum_guarantee_vm_bandwidth()
