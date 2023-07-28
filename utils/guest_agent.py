"""
Module for interacting with VMs using qemu guest agent.
"""
import subprocess
import json
import os
import base64


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


def file_open(vm_name, file_path, mode):
    open_command_args = {
        "execute": "guest-file-open",
        "arguments": {
            "path": file_path,
            "mode": mode
        }
    }
    handle_id = qemu_agent_command(vm_name, open_command_args)['return']
    return handle_id


def file_write(vm_name, content, handle_id):
    # Write to the file
    write_command_args = {
        "execute": "guest-file-write",
        "arguments": {
            "handle": handle_id,
            "buf-b64": base64.b64encode(content.encode()).decode()
        }
    }
    qemu_agent_command(vm_name, write_command_args)


def file_read(vm_name, handle_id):
    # Read from the file
    read_command_args = {
        "execute": "guest-file-read",
        "arguments": {
            "handle": handle_id
        }
    }
    data = qemu_agent_command(vm_name, read_command_args)

    # Decode the base64-encoded data
    content = base64.b64decode(data['return']['buf-b64']).decode()

    return content


def file_close(vm_name, handle_id):
    # Close the file
    close_command_args = {
        "execute": "guest-file-close",
        "arguments": {
            "handle": handle_id
        }
    }
    qemu_agent_command(vm_name, close_command_args)


def read_file(vm_name, file_path):
    # Open the file
    handle_id = file_open(vm_name, file_path, "r")

    # Read from the file
    content = file_read(vm_name, handle_id)

    # Close the file
    file_close(vm_name, handle_id)

    return content


def copy_file(vm_name, host_file_path, guest_dir):
    # Extract the file name from the host file path
    file_name = os.path.basename(host_file_path)

    # Construct the full path on the guest
    guest_file_path = os.path.join(guest_dir, file_name)

    # Read the content of the file
    with open(host_file_path, 'r') as file:
        content = file.read()

    # Ensure the directory exists on the VM
    exec(vm_name, f"mkdir -p {os.path.dirname(guest_file_path)}")

    # Open the file on the VM
    handle_id = file_open(vm_name, guest_file_path, "w+")

    # Write to the file on the VM
    file_write(vm_name, content, handle_id)

    # Close the file on the VM
    file_close(vm_name, handle_id)


def copy_directory(vm_name, local_dir, vm_dir):
    # Iterate over each file in the directory
    for root, dirs, files in os.walk(local_dir):
        for file in files:
            # Construct the full path to the file
            local_file_path = os.path.join(root, file)

            # Read the content of the file
            with open(local_file_path, 'rb') as f:
                content = f.read()

            # Construct the corresponding path in the VM
            relative_path = os.path.relpath(local_file_path, local_dir)
            vm_file_path = os.path.join(vm_dir, relative_path)

            # Ensure the directory exists in the VM
            vm_file_dir = os.path.dirname(vm_file_path)
            exec(vm_name, f"mkdir -p {vm_file_dir}")

            # Copy the file to the VM
            copy_file(vm_name, vm_file_path, content)
