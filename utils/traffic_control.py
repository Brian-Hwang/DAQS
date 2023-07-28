"""
Module for controlling network traffic of VMs.
"""
from utils import guest_agent


def delete_queue_discipline(vm_name, interface):
    """
    Deletes the queuing discipline for a VM's network interface.
    """
    command = f"sudo tc qdisc del dev {interface} root"
    guest_agent.exec(vm_name, command)


def add_queue_discipline(vm_name, interface):
    """
    Adds a queuing discipline to a VM's network interface.
    """
    command = f"sudo tc qdisc add dev {interface} root handle 1: htb default 10"
    guest_agent.exec(vm_name, command)


def limit_class_bandwidth(vm_name, interface, bw_limit):
    """
    Limits the bandwidth of class 1 traffic on a VM's network interface.
    """
    command = f"sudo tc class add dev {interface} parent 1:1 classid 1:10 htb rate {bw_limit}Gbit"
    guest_agent.exec(vm_name, command)


def delete_class_bandwidth(vm_name, interface):
    """
    Deletes the bandwidth limit of class 1 traffic on a VM's network interface.
    """
    command = f"sudo tc class del dev {interface} classid 1:1"
    guest_agent.exec(vm_name, command)


def initialize(vm_name, interface):
    """
    Initializes the traffic control settings for a VM's network interface.
    """
    delete_queue_discipline(vm_name, interface)
    add_queue_discipline(vm_name, interface)


def set_bandwidth_limit(vm_name, interface, bw_limit, is_initialized=False):
    """
    Limits the bandwidth of a VM's network interface.
    If the VM has not been initialized, it initializes the VM first.
    """
    if not is_initialized:
        initialize(vm_name, interface)
    else:
        delete_class_bandwidth(vm_name, interface)
    limit_class_bandwidth(vm_name, interface, bw_limit)
