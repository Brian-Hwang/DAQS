import subprocess


def get_running_vms():
    command = ['sudo', 'virsh', 'list', '--state-running']
    output = subprocess.run(command, capture_output=True, text=True)

    if output.returncode != 0:
        print(f"Command failed with error:\n{output.stderr}")
        return None

    lines = output.stdout.splitlines()
    vm_names = []

    # skip the header lines
    for line in lines[2:]:
        if not line.strip():  # Skip the last line if it's empty
            continue
        fields = line.split()
        # the second field is the VM name
        vm_names.append(fields[1])

    return set(vm_names)


# TODO: Get the VF name using the VM name
def get_vf_using_vms():
    vm_names = get_running_vms()
    for vm in vm_names:
        # Command to get the XML definition for the VM
        dumpxml_command = ["sudo", "virsh", "dumpxml", vm]

        # Get the output from the command
        xml_output = subprocess.run(
            dumpxml_command, capture_output=True, text=True)

        print(xml_output.stdout)
        # If the XML contains <source address=, print the VM name
        if '<source address=' in xml_output.stdout:
            print(vm)
