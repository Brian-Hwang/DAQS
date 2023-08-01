import time
import datetime
import utils.guest_manager as gm
import utils.traffic_control as tc
import utils.guest_utils as guest
import utils.host_utils as host
import utils.read_config as cfg

IGNORE_BW_THRESHOLD_GBPS = 1
MARGINAL_RATE = 1.1
MARGINAL_OFFEST = 0
STEP_GBPS = 1


def limit_best_effort_vm_bandwidth(vms, interfaces, regulated_speed, guaranteed_vms, host_bandwidth):
    """
    Function to limit the bandwidth of Best-Effort VMs.
    """
    if regulated_speed > 0:
        for vm in vms:
            if vm in guaranteed_vms.keys():
                continue
            tc.set_bandwidth_limit(vm, interfaces[vm], regulated_speed)
    elif regulated_speed == -1:
        for vm in vms:
            tc.delete_queue_discipline(vm, interfaces[vm])


def minimum_guarantee_vm_bandwidth():
    """
    Function to manage the minimum bandwidth for VMs.
    It continuously monitors the VMs and adjusts their bandwidth.
    """
    host_interface = cfg.read_host_interface()
    host_bandwidth = host.get_bandwidth(host_interface)

    guaranteed_vms = cfg.read_guaranteed_vms()
    print(f"Manager init. Guaranteed VMs: {guaranteed_vms}")

    vms = {}
    regulated_speed = -1
    prev_vms = set()

    while True:
        start_time = time.perf_counter()

        running_vms = host.get_running_vms()
        if running_vms is None:
            continue

        if running_vms != prev_vms or not vms:
            interfaces = {}
            ready_vms = set()

            for vm in running_vms:
                while True:
                    try:
                        interfaces[vm] = guest.get_last_network_interface(vm)
                        vms[vm] = gm.GuestManager(vm)
                        ready_vms.add(vm)
                        break
                    except TypeError:
                        print(f"VM {vm} is not fully ready. Waiting...")
                        time.sleep(1)

            guaranteed_speed = 0
            for name, spd in guaranteed_vms.items():
                if name in ready_vms:
                    guaranteed_speed += spd

            current_speed = 0
            total_speed = 0
            for vm in ready_vms:
                spd = vms[vm].get_tx_speed_mbps() / (2.0**10)
                if vm in guaranteed_vms.keys():
                    current_speed += spd
                    total_speed += spd
                else:
                    total_speed += spd

            if current_speed < IGNORE_BW_THRESHOLD_GBPS:
                regulated_speed = -1
            elif current_speed < guaranteed_speed:
                if regulated_speed == -1:
                    regulated_speed = host_bandwidth - guaranteed_speed
                else:
                    regulated_speed -= STEP_GBPS
                    if regulated_speed <= 0:
                        regulated_speed = -1
            elif current_speed > guaranteed_speed * MARGINAL_RATE + MARGINAL_OFFEST:
                if total_speed - current_speed > IGNORE_BW_THRESHOLD_GBPS:
                    regulated_speed += STEP_GBPS
                    if regulated_speed > host_bandwidth - guaranteed_speed:
                        regulated_speed = host_bandwidth - guaranteed_speed

            limit_best_effort_vm_bandwidth(
                ready_vms, interfaces, regulated_speed, guaranteed_vms, host_bandwidth)

            print(
                f"Total speed {total_speed}, guaranteed group {current_speed}, regulated speed {regulated_speed}")

            prev_vms = ready_vms

        elapsed_time = time.perf_counter() - start_time
        sleep_time = max(0, 1 - elapsed_time)
        time.sleep(sleep_time)


if __name__ == "__main__":
    minimum_guarantee_vm_bandwidth()
