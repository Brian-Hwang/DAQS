import os
import time
import inspect
import subprocess
import utils.guest_agent as guest_agent
import utils.host_utils as host
import utils.read_config as cfg

test_name = "test1-baseline"


def N_vs_N():

    guest_base_path = cfg.read_guest_base_directory()

    vm_names = host.get_running_vms()
    if vm_names is None:
        return

    for vm_name in vm_names:
        guest_agent.exec(
            vm_name, f"python3 {guest_base_path}/iperf_test.py -u 120 -s 5 -e 5 -t 10&")

    # Wait for 25 minutes
    time.sleep(13 * 120)

    host_base_path = cfg.read_host_base_directory()

    current_function_name = inspect.currentframe().f_code.co_name

    for vm_name in vm_names:
        # Read the result from the VM
        result = guest_agent.read_file(
            vm_name, f"{guest_base_path}/results.txt")

        # Save the result to a file
        with open(f"{host_base_path}/test/{test_name}/results/results.txt", 'w') as file:
            file.write(result)

        subprocess.run(["python3", host_base_path + "/test/scripts/to_csv.py", "-i", f"{host_base_path}/test/{test_name}/results/results.txt", "-o",
                        f"{host_base_path}/test/{test_name}/results/result_{vm_name}_{current_function_name}.csv"])


def N_vs_1():
    guest_base_path = cfg.read_guest_base_directory()

    vm_names = host.get_running_vms()
    if vm_names is None:
        return

    for vm_name in vm_names:
        if vm_name != "b1_vm1":
            guest_agent.exec(
                vm_name, f"python3 {guest_base_path}/iperf_test.py -u 120 -i 20.0.1.26 -s 5 -e 5 -t 10 &")
        else:
            guest_agent.exec(
                vm_name, f"python3 {guest_base_path}/iperf_test.py -u 120 -i 20.0.1.27 -s 2 -e 2 -t 10 &")

    # Wait for 30 minutes
    time.sleep(23 * 60)

    host_base_path = cfg.read_host_base_directory()

    current_function_name = inspect.currentframe().f_code.co_name

    for vm_name in vm_names:
        # Read the result from the VM
        result = guest_agent.read_file(
            vm_name, f"{guest_base_path}/results.txt")

        # Save the result to a file
        with open(f"{host_base_path}/test/{test_name}/results/results.txt", 'w') as file:
            file.write(result)

        subprocess.run(["python3", host_base_path + "/test/scripts/to_csv.py", "-i", f"{host_base_path}/test/{test_name}/results/results.txt", "-o",
                        f"{host_base_path}/test/{test_name}/results/result_{vm_name}_{current_function_name}.csv"])


def main():
    iperf_test_file_path = cfg.read_host_base_directory() + "/test/scripts/iperf_test.py"
    guest_file_path = cfg.read_guest_base_directory()
    vm_names = host.get_running_vms()
    if vm_names is None:
        return

    for vm_name in vm_names:
        guest_agent.copy_file(vm_name, iperf_test_file_path, guest_file_path)

    # N_vs_N()
    N_vs_1()


if __name__ == "__main__":
    main()
