import time
from datetime import datetime
import utils.traffic_control as tc
import utils.guest_utils as guest
import utils.host_utils as host
import utils.read_config as cfg


class MinBandwidthManager:

    def __init__(self, config_path="config.ini"):
        self.host_interface = cfg.read_host_interface(config_path)
        self.host_bandwidth = host.get_bandwidth(self.host_interface)

        self.prev_vm_names = set()
        self.initialized_vms = set()

        self.period = 1 # 주기 1초
        self.last_time = datetime.time()

    def start(self):
        self.last_time = datetime.time()
        self.run()


    def schedule_run(self):
        # 주기적으로 실행하게끔 시간 보정
        while True:
            # 이미 주기가 지났다면 한 주기 더 대기
            if datetime.time() - self.last_time > self.period:
                self.last_time += self.period
                continue            
            time.sleep(self.period - (datetime.time() - self.last_time))
            self.last_time = datetime.time()
            self.run()

    
    def run(self):
        vms = host.get_running_vms()
        if vms is None:
            self.schedule_run()


if __name__ == "__main__":
    MinBandwidthManager()

       
"""
def limit_vm_bandwidth_evenly(vm_names, interfaces, total_bandwidth, initialized_vms):
    
    #Function to limit the bandwidth of virtual machines evenly.
    #vm_names: list of names of the VMs
    #interfaces: mapping of VM names to their respective interfaces
    #total_bandwidth: total bandwidth available
    #initialized_vms: set of VMs that have been initialized

    bw_limit_per_vm = total_bandwidth // len(vm_names)

    for vm_name in vm_names:
        is_initialized = vm_name in initialized_vms
        tc.set_bandwidth_limit(
            vm_name, interfaces[vm_name], bw_limit_per_vm, is_initialized)
        initialized_vms.add(vm_name)


def fair_share_vm_bandwidth():

    #Function to manage the bandwidth of VMs.
    #It continuously monitors the VMs and adjusts their bandwidth.

    host_interface = cfg.read_host_interface()
    host_bandwidth = host.get_bandwidth(host_interface)

    prev_vm_names = set()
    initialized_vms = set()

    while True:
        time.sleep(1)

        vm_names = host.get_running_vms()
        if vm_names is None:
            continue

        if vm_names != prev_vm_names or not initialized_vms:
            interfaces = {}
            ready_vms = set()

            for vm_name in vm_names:
                while True:
                    try:
                        interfaces[vm_name] = guest.get_last_network_interface(
                            vm_name)
                        ready_vms.add(vm_name)
                        break
                    except TypeError:
                        print(f"VM {vm_name} is not fully ready. Waiting...")
                        time.sleep(1)
            if len(ready_vms) == 1:
                vm_name = next(iter(ready_vms))  # get the only VM
                tc.delete_queue_discipline(vm_name, interfaces[vm_name])
                initialized_vms.discard(vm_name)
            else:
                limit_vm_bandwidth_evenly(
                    ready_vms, interfaces, host_bandwidth, initialized_vms)

            initialized_vms = initialized_vms.intersection(ready_vms)
            prev_vm_names = ready_vms
"""

