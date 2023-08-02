import time
import inspect
import threading
import subprocess
import utils.guest_agent as guest_agent
import utils.host_utils as host
import utils.read_config as cfg
import models.multi_tenants.min_bw_legacy as min_bw_legacy
test_name = "test4-minimumguarantee"


def N_vs_N():

    guest_base_path = cfg.read_guest_base_directory()

    vm_names = host.get_running_vms()
    if vm_names is None:
        return

    for vm_name in vm_names:
        guest_agent.exec(
            vm_name, f"python3 {guest_base_path}/iperf_test.py -t 1 &")

    # Wait for 30 minutes
    time.sleep(30 * 60)

    host_base_path = cfg.read_host_base_directory()

    current_file_name = __file__
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


def N_vs_one():
    guest_base_path = cfg.read_guest_base_directory()

    vm_names = host.get_running_vms()
    if vm_names is None:
        return

    counter = 0
    for vm_name in vm_names:
        counter += 1
        if counter % 2 == 0:
            guest_agent.exec(
                vm_name, f"python3 {guest_base_path}/iperf_test.py &")
        if counter % 2 == 1:
            guest_agent.exec(
                vm_name, f"python3 {guest_base_path}/iperf_test.py -l nothing &")

    # Wait for 30 minutes
    time.sleep(30 * 60)

    host_base_path = cfg.read_host_base_directory()

    current_file_name = __file__
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


def one_vs_N():
    guest_base_path = cfg.read_guest_base_directory()

    vm_names = host.get_running_vms()
    if vm_names is None:
        return

    counter = 0
    for vm_name in vm_names:
        counter += 1
        if counter % 2 == 1:
            guest_agent.exec(
                vm_name, f"python3 {guest_base_path}/iperf_test.py &")
        if counter % 2 == 0:
            guest_agent.exec(
                vm_name, f"python3 {guest_base_path}/iperf_test.py -l nothing &")

    # Wait for 30 minutes
    time.sleep(30 * 60)

    host_base_path = cfg.read_host_base_directory()

    current_file_name = __file__
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
    thread = threading.Thread(
        target=min_bw_legacy.run_min_bw)
    thread.start()

    iperf_test_file_path = cfg.read_host_base_directory() + "/test/scripts/iperf_test.py"
    guest_file_path = cfg.read_guest_base_directory()
    vm_names = host.get_running_vms()
    if vm_names is None:
        return

    for vm_name in vm_names:
        guest_agent.copy_file(vm_name, iperf_test_file_path, guest_file_path)

    N_vs_N()
    N_vs_one()
    one_vs_N()


if __name__ == "__main__":
    main()
