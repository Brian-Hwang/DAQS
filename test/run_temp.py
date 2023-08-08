import time
import os
import argparse
import threading
import multiprocessing
import subprocess
import utils.guest_agent as guest_agent
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

    print(f"Start test for {vm_names}...")

    for vm_name in vm_names:
        current_parallel = args.parallel
        if vm_name in ["b1_vm1"]:
            current_parallel = 2
        guest_agent.exec(vm_name, f"python3 {guest_base_path}/iperf_test.py -s {current_parallel} -e {current_parallel} -t {args.test_times} -u {args.duration} -l parallel &")

    time.sleep(args.duration * args.test_times + (args.test_times + 1))

    print("Test finished. Collecting results...")

    current_file_name = __file__
    current_loc = os.path.dirname(os.path.abspath(current_file_name))

    for vm_name in vm_names:
        # Read the result from the VM
        result = guest_agent.read_file(
            vm_name, f"{guest_base_path}/results.txt")

        # Save the result to a file
        with open(f"{current_loc}/test_tmp_result_{vm_name}.txt", 'w') as file:
            file.write(result)

        print(f"Result for {vm_name}: \n{result}")
        # subprocess.run(["python3", host_base_path + "/test/scripts/to_csv.py", "-i", f"{host_base_path}/test/{test_name}/results/results.txt", "-o",
        #                f"{host_base_path}/test/{test_name}/results/result_{vm_name}_{current_function_name}.csv"])

    return


def main(args):
    proc = multiprocessing.Process(
        target = minimum_guarantee.minimum_guarantee_vm_bandwidth, args = ())
    proc.start()

    iperf_test_file_path = cfg.read_host_base_directory() + "/test/scripts/iperf_test.py"
    guest_file_path = cfg.read_guest_base_directory()
    vm_names = host.get_running_vms()
    if vm_names is None:
        return

    for vm_name in vm_names:
        guest_agent.copy_file(vm_name, iperf_test_file_path, guest_file_path)

    do_test(args)
    proc.terminate()

# Default values
default_values = {
    "duration": 120,
    "parallel": 5,
    "test_times": 10,
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--duration", default=default_values["duration"], type=int, help=f"test duration (default: {default_values['duration']})")
    parser.add_argument("-p", "--parallel", default=default_values["parallel"], type=int,
                        help=f"parallel of iperf (default: {default_values['parallel']})")
    parser.add_argument("-t", "--test_times", default=default_values["test_times"], type=int,
                        help=f"iterate times (default: {default_values['test_times']})")


    args = parser.parse_args()
    main(args)