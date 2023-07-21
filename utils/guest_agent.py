import subprocess
import json


def qemu_agent_command(vm_name, command_args):
    cmd = [
        "sudo", "virsh", "qemu-agent-command", vm_name,
        json.dumps(command_args), "--pretty"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)

    return data


def guest_network_get_interfaces(vm_name):
    command_args = {"execute": "guest-network-get-interfaces"}
    data = qemu_agent_command(vm_name, command_args)

    return data


def guest_exec(vm_name, command):
    command_args = {
        "execute": "guest-exec",
        "arguments": {
            "path": "/bin/bash",
            "arg": ["-c", command],
            "capture-output": True
        }
    }
    qemu_agent_command(vm_name, command_args)
