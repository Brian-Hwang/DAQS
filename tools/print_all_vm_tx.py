import time
import threading
import utils.traffic_control as tc
import utils.guest_utils as guest
import utils.host_utils as host


def main():
    conditions = []
    threads = {}

    while True:
        time.sleep(1)  # Check for new VMs every second

        # Get running VMs
        vm_names = host.get_running_vms()
        print(vm_names)

        for vm_name in vm_names:
            if vm_name not in threads:
                # Get the last interface
                interface = guest.get_last_network_interface(vm_name)

                # Create a new condition for the new VM
                condition = threading.Condition()
                conditions.append(condition)

                # The next condition is the condition of the next VM, or the first VM if this is the last VM
                next_condition = conditions[0] if conditions else condition

                # Start a new thread for the new VM
                thread = threading.Thread(target=guest.print_gbits, args=(
                    vm_name, interface, condition, next_condition))
                thread.start()
                threads[vm_name] = thread, condition

        # Stop threads for VMs that are no longer running
        # Make a copy of the list because we're going to modify it
        for vm_name in list(threads):
            if vm_name not in vm_names:
                thread, condition = threads[vm_name]
                with condition:
                    condition.notify()  # Notify the thread that it can exit
                thread.join()
                del threads[vm_name]
                conditions.remove(condition)

        # If there are any threads, notify the first one that it's their turn to print
        if conditions:
            with conditions[0]:
                conditions[0].notify()


if __name__ == "__main__":
    main()
