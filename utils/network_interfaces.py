from utils.guest_agent import guest_network_get_interfaces


def last_network_interface(vm_name):
    data = guest_network_get_interfaces(vm_name)
    return data["return"][-1]["name"]


def check_tc_byte(vm_name, interface):
    data = guest_network_get_interfaces(vm_name)

    # Find the interface by name
    for iface in data["return"]:
        if iface["name"] == interface:
            tx_bytes = int(iface["tx-bytes"])
            return tx_bytes

    return 0


def check_tc_Gbits(vm_name, interface):
    tx_bytes = check_tc_byte(vm_name, interface)

    # Convert bytes to Gbits
    tx_Gbits = tx_bytes / (2**30) * 8
    return tx_Gbits
