import utils.traffic_control as tc
import utils.guest_utils as guest
import utils.host_utils as host
import utils.read_config as cfg


def main():
    """
    Main function to limit the bandwidth of a running VM.
    """

    # Read host interface and bandwidth from config
    host_interface = cfg.read_host_interface()
    host_bandwidth = host.get_bandwidth(host_interface)

    # Set bandwidth limit
    bw_limit = host_bandwidth / 2

    # Get running VMs
    running_vms = host.get_running_vms()

    # Check if there are any running VMs
    if not running_vms:
        print("No running VMs found.")
        return

    # Select first running VM
    vm_name = list(running_vms)[0]

    # Get the last interface of the selected VM
    interface = guest.get_last_network_interface(vm_name)

    # Limit the bandwidth of the selected VM
    tc.set_bandwidth_limit_once(vm_name, interface, bw_limit)
    # tc.set_bandwidth_limit(vm_name, interface, bw_limit)


if __name__ == "__main__":
    main()
