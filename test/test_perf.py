import time
import os
import argparse
import threading
import multiprocessing
import subprocess
import utils.traffic_control as tc
import utils.guest_agent as guest_agent
import utils.guest_utils as guest
import utils.host_utils as host
import utils.read_config as cfg
import models.multi_tenants.min_bw_legacy as min_bw_legacy
import models.multi_tenants.minimum_guarantee as minimum_guarantee
test_name = "test-tmp"


def do_test(args):
    guest_base_path = cfg.read_guest_base_directory()

    vm_names = host.get_running_vms()
    if vm_names is None:
        return

    for vm_name in vm_names:
        guest_agent.exec(vm_name, f"python3 {guest_base_path}/iperf_test.py -s 2 -e 4 -t 3 -u 60 &")

    time.sleep(60*3*3 + 3)

    current_file_name = __file__
    current_loc = os.path.dirname(os.path.abspath(current_file_name))

    for vm_name in vm_names:
        # Read the result from the VM
        result = guest_agent.read_file(
            vm_name, f"{guest_base_path}/results.txt")

        print(f"Result for {vm_name}: {result}")
        # subprocess.run(["python3", host_base_path + "/test/scripts/to_csv.py", "-i", f"{host_base_path}/test/{test_name}/results/results.txt", "-o",
        #                f"{host_base_path}/test/{test_name}/results/result_{vm_name}_{current_function_name}.csv"])

    return


def main(args):
    iperf_test_file_path = cfg.read_host_base_directory() + "/test/scripts/iperf_test.py"
    guest_file_path = cfg.read_guest_base_directory()
    vm_names = host.get_running_vms()
    if vm_names is None:
        return

    for vm_name in vm_names:
        guest_agent.copy_file(vm_name, iperf_test_file_path, guest_file_path)

    restrict_vm_name = "ubuntu20.04-clone2"
    restrict_vm_iface = guest.get_last_network_interface(vm_name)
    for tc_gbps in range(5, 9, 0.5):
        tc.set_bandwidth_limit_mbps(
            restrict_vm_name, restrict_vm_iface, tc_gbps * (2.0**10))
        print(f"{tc_gbps} Gbps limit: ")
        do_test(args)
        print("========================")

    tc.delete_queue_discipline(restrict_vm_name, restrict_vm_iface)
    print(f"no limit: ")
    do_test(args)
    print("========================")

# Default values
default_values = {
    "duration": 60,
    "parallel": 1,
    "test_times": 10,
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--duration", default=default_values["duration"], type=int, help=f"test duration (default: {default_values['duration']})")
    #parser.add_argument("-p", "--parallel", default=default_values["parallel"], type=int,
    #                    help=f"parallel of iperf (default: {default_values['parallel']})")
    parser.add_argument("-t", "--test_times", default=default_values["test_times"], type=int,
                        help=f"iterate times (default: {default_values['test_times']})")


    args = parser.parse_args()
    main(args)