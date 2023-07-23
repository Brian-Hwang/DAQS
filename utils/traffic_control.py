from GA.utils.guest_agent import guest_exec


def tc_del_qdisc(vm_name, interface):
    command = "sudo tc qdisc del dev {interface} root".format(
        interface=interface)
    guest_exec(vm_name, command)


def tc_add_qdisc(vm_name, interface):
    command = "sudo tc qdisc add dev {interface} root handle 1: htb default 10".format(
        interface=interface)
    guest_exec(vm_name, command)


def tc_class1_limit_bandwidth(vm_name, interface, bw_limit):
    command = "sudo tc class add dev {interface} parent 1: classid 1:1 htb rate {bw_limit}".format(
        interface=interface, bw_limit=bw_limit)
    guest_exec(vm_name, command)


def tc_class10_limit_bandwidth(vm_name, interface, bw_limit):
    command = "sudo tc class add dev {interface} parent 1:1 classid 1:10 htb rate {bw_limit}".format(
        interface=interface, bw_limit=bw_limit)
    guest_exec(vm_name, command)


def tc_init(vm_name, interface):
    tc_del_qdisc(vm_name, interface)
    tc_add_qdisc(vm_name, interface)


def tc_limit_bandwidth(vm_name, interface, bw_limit):
    tc_class1_limit_bandwidth(vm_name, interface, bw_limit)
    tc_class10_limit_bandwidth(vm_name, interface, bw_limit)
