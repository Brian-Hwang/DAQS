"""
Module for utility functions related to VMs.
"""
from utils import guest_agent


def get_last_network_interface(vm_name):
    """
    Gets the last network interface of a VM.
    """
    data = guest_agent.network_get_interfaces(vm_name)
    return data["return"][-1]["name"]


def check_tx_bytes(vm_name, interface):
    """
    Checks the number of bytes transmitted by a VM's network interface.
    """
    data = guest_agent.network_get_interfaces(vm_name)
    for iface in data["return"]:
        if iface["name"] == interface:
            tx_bytes = int(iface["statistics"]["tx-bytes"])
            return tx_bytes
    return 0


def check_tx_gbits(vm_name, interface):
    """
    Checks the amount of data transmitted by a VM's network interface in Gbits.
    """
    tx_bytes = check_tx_bytes(vm_name, interface)
    tx_gbits = tx_bytes / (2**30) * 8
    return tx_gbits
