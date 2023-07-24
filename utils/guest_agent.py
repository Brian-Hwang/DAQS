"""
Module for interacting with VMs using qemu guest agent.
"""
import subprocess
import json


def qemu_agent_command(vm_name, command_args):
    cmd = [
        "sudo", "virsh", "qemu-agent-command", vm_name,
        json.dumps(command_args), "--pretty"
    ]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)

    # Wait for the process to complete and get the output
    stdout, _ = process.communicate()

    if process.returncode != 0:
        print(f"Command failed with return code {process.returncode}")
        return None

    data = json.loads(stdout)
    return data


def network_get_interfaces(vm_name):
    """
    Gets network interfaces of a VM.
    """
    command_args = {"execute": "guest-network-get-interfaces"}
    data = qemu_agent_command(vm_name, command_args)
    return data


def exec(vm_name, command):
    """
    Executes a command inside a VM.
    """
    command_args = {"execute": "guest-exec", "arguments": {"path": "/bin/bash",
                                                           "arg": ["-c", command], "capture-output": True}}
    data = qemu_agent_command(vm_name, command_args)
    return data
