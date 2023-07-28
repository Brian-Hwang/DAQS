import os
import time
import inspect
import subprocess
import utils.guest_agent as guest_agent
import utils.host_utils as host
import utils.read_config as cfg


def N_versus_N():

    guest_base_path = cfg.read_guest_base_directory()

    vm_names = host.get_running_vms()
    if vm_names is None:
        return

    for vm_name in vm_names:
        guest_agent.exec(vm_name, f"python3 {guest_base_path}/iperf_test.py &")

    # Wait for 25 minutes
    time.sleep(25 * 60)

    host_base_path = cfg.read_host_base_directory()

    current_file_name = __file__
    current_function_name = inspect.currentframe().f_code.co_name

    for vm_name in vm_names:
        # Read the result from the VM
        result = guest_agent.read_file(
            vm_name, f"{guest_base_path}/result.txt")

        # Save the result to a file
        with open(f"result.txt", 'w') as file:
            file.write(result)

        subprocess.run(["scp", "result.txt", host_base_path +
                       "/test/scripts/to_csv.py"])
        os.rename(
            "result.txt", f"result_{vm_name}_{current_file_name}_{current_function_name}.txt")


def N_versus_1():
    return


def main():
    iperf_test_file_path = cfg.read_host_base_directory() + "/test/scripts/iperf_test.py"
    guest_file_path = cfg.read_guest_base_directory()
    vm_names = host.get_running_vms()
    if vm_names is None:
        return

    for vm_name in vm_names:
        guest_agent.copy_file(vm_name, iperf_test_file_path, guest_file_path)

    for vm_name in vm_names:
        print(guest_agent.read_file(vm_name, "/home/user/iperf_test.py"))
    # N_versus_N()
    # N_versus_1()


if __name__ == "__main__":
    main()
