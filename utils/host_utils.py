"""
Module for utility functions related to the host machine.
"""
import subprocess


def get_vms():
    """
    Gets a list of all VMs.
    """
    command = ['sudo', 'virsh', 'list', '--all']
    output = subprocess.run(command, capture_output=True, text=True)
    if output.returncode != 0:
        raise Exception(f"Command failed with error:\n{output.stderr}")
    lines = output.stdout.splitlines()
    vm_names = {line.split()[1] for line in lines[2:] if line.strip()}
    return vm_names


def get_running_vms():
    """
    Gets a list of currently running VMs.
    """
    command = ['sudo', 'virsh', 'list', '--state-running']
    output = subprocess.run(command, capture_output=True, text=True)
    if output.returncode != 0:
        raise Exception(f"Command failed with error:\n{output.stderr}")
    lines = output.stdout.splitlines()
    vm_names = {line.split()[1] for line in lines[2:] if line.strip()}
    return vm_names


def get_vf_using_vms():
    """
    Prints VMs that have a virtual function.
    """
    vm_names = get_running_vms()
    for vm in vm_names:
        dumpxml_command = ["sudo", "virsh", "dumpxml", vm]
        xml_output = subprocess.run(
            dumpxml_command, capture_output=True, text=True).stdout
        if '<source address=' in xml_output:
            print(vm)


def start_first_non_running_vm():
    all_vms = get_vms()
    running_vms = get_running_vms()

    for vm in all_vms:
        if vm not in running_vms:
            command = ['sudo', 'virsh', 'start', vm]
            output = subprocess.run(command, capture_output=True, text=True)
            if output.returncode != 0:
                raise Exception(f"Command failed with error:\n{output.stderr}")
            else:
                print(f"VM {vm} started successfully")
            return
    print("No non-running VMs found.")


def get_bandwidth(interface):
    """
    Gets the bandwidth of a network interface on the host machine.
    """
    command = ['sudo', 'ethtool', interface]
    output = subprocess.run(command, capture_output=True, text=True)
    if output.returncode != 0:
        raise Exception(f"Command failed with error:\n{output.stderr}")
    for line in output.stdout.splitlines():
        line = line.strip()
        if line.startswith('Speed:'):
            speed_str = line.split()[1]
            speed_value, speed_unit = speed_str[:-4], speed_str[-4:]
            speed_value = int(speed_value)
            if speed_unit == 'Mb/s':
                speed_value //= 1000
            return speed_value
    return None
